# src/persistence/repos/jobs_repo.py

import json
from sqlite3 import IntegrityError
from typing import Optional
from persistence.models import JobRecord
from persistence.errors import JobNotFoundError
from scoring.ai_relevance_explainer import generate_ai_relevance_explanation
from discovery.title_signal_extractor import extract_title_signals


class JobsRepo:

    def __init__(self, conn):
        self.conn = conn

    def list_new_jobs_since(self, since_iso: str) -> list[JobRecord]:
        rows = self.conn.execute(
            """
            SELECT *
            FROM jobs
            WHERE first_seen_at IS NOT NULL
              AND first_seen_at > ?
              AND is_archived = 0
            ORDER BY first_seen_at DESC
            """,
            (since_iso,),
        ).fetchall()

        return [JobRecord(**row) for row in rows]

    def count_jobs_since(self, timestamp: str) -> int:
        row = self.conn.execute(
            """
            SELECT COUNT(*)
            FROM jobs
            WHERE is_archived = 0
              AND discovered_at > ?
            """,
            (timestamp,),
        ).fetchone()
        return int(row[0]) if row else 0

    def upsert_discovered_job(
        self,
        provider: str,
        external_id: str,
        provider_job_key: str,
        company: str,
        title: str,
        location_raw: Optional[str],
        location_norm: Optional[str],
        url: str,
        posted_at: Optional[str],
        discovered_at: str,
        raw_provider_payload_json: Optional[str],
    ) -> JobRecord:

        try:
            self.conn.execute(
                """
                INSERT INTO jobs (
                    provider, external_id, provider_job_key,
                    company, title, location_raw, location_norm,
                    url, posted_at, discovered_at,
                    raw_provider_payload_json,
                    first_seen_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    provider,
                    external_id,
                    provider_job_key,
                    company,
                    title,
                    location_raw,
                    location_norm,
                    url,
                    posted_at,
                    discovered_at,
                    raw_provider_payload_json,
                    discovered_at,  # first_seen_at set only on insert
                ),
            )
        except IntegrityError:
            # update metadata only
            self.conn.execute(
                """
                UPDATE jobs
                SET company = ?,
                    title = ?,
                    location_raw = ?,
                    location_norm = ?,
                    url = ?,
                    posted_at = ?,
                    raw_provider_payload_json = ?
                WHERE provider_job_key = ?
                """,
                (
                    company,
                    title,
                    location_raw,
                    location_norm,
                    url,
                    posted_at,
                    raw_provider_payload_json,
                    provider_job_key,
                ),
            )

        row = self.conn.execute(
            "SELECT * FROM jobs WHERE provider_job_key = ?",
            (provider_job_key,),
        ).fetchone()

        return JobRecord(**row)

    def list_discovery_feed_jobs(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        location: Optional[str] = None,
        role: Optional[str] = None,
        experience: Optional[str] = None,
        company: Optional[str] = None,
        ai_filter: Optional[str] = None,
        signal: Optional[str] = None,
        signals: Optional[list[str]] = None,
    ) -> tuple[list[dict], int]:
        where, params = self._build_discovery_where_and_params(
            location=location,
            role=role,
            experience=experience,
            company=company,
            ai_filter=ai_filter,
            signal=signal,
            signals=signals,
        )
        ranking_expr, ranking_params = self._build_role_ranking_expression(role)

        page = max(1, page)
        page_size = max(1, page_size)
        offset = (page - 1) * page_size

        count_row = self.conn.execute(
            f"""
            SELECT COUNT(*)
            FROM jobs
            LEFT JOIN job_user_state
              ON jobs.provider_job_key = job_user_state.job_id
            WHERE {' AND '.join(where)}
              AND (
                job_user_state.state IS NULL
                OR job_user_state.state = 'discovered'
              )
            """,
            tuple(params),
        ).fetchone()
        total_jobs = int(count_row[0]) if count_row else 0

        paged_params = list(params)
        paged_params.extend(ranking_params)
        paged_params.extend([page_size, offset])
        order_by = (
            f"({ranking_expr}) DESC, jobs.discovered_at DESC"
            if ranking_expr
            else "jobs.discovered_at DESC"
        )

        rows = self.conn.execute(
            f"""
            SELECT
              jobs.provider_job_key,
              jobs.company,
              jobs.title,
              jobs.location_raw,
              jobs.url,
              jobs.posted_at,
              jobs.provider,
              job_user_state.state,
              jobs.raw_provider_payload_json,
              ji.interpretation_json
            FROM jobs
            LEFT JOIN job_user_state
              ON jobs.provider_job_key = job_user_state.job_id
            LEFT JOIN job_interpretations ji
              ON jobs.provider_job_key = ji.job_id
            WHERE {' AND '.join(where)}
              AND (
                job_user_state.state IS NULL
                OR job_user_state.state = 'discovered'
              )
            ORDER BY {order_by}
            LIMIT ?
            OFFSET ?
            """,
            tuple(paged_params),
        ).fetchall()

        jobs: list[dict] = []
        for row in rows:
            raw_provider_payload_json = row[8]
            interpretation_json = row[9]

            ai_relevance_score = self._extract_ai_relevance_score(raw_provider_payload_json)
            interpretation = self._safe_json_loads(interpretation_json)
            ai_relevance_explanation = generate_ai_relevance_explanation(
                interpretation if isinstance(interpretation, dict) else {},
                ai_relevance_score,
            )
            signals = self._extract_persisted_signals(
                raw_provider_payload_json=raw_provider_payload_json,
                title=row[2] or "",
            )

            jobs.append(
                {
                    "job_id": row[0],
                    "company": row[1],
                    "title": row[2],
                    "location": row[3],
                    "url": row[4],
                    "posted_at": row[5],
                    "provider": row[6],
                    "state": row[7],
                    "ai_relevance_score": ai_relevance_score,
                    "ai_relevance_explanation": ai_relevance_explanation,
                    "signals": signals,
                }
            )
        return jobs, total_jobs

    def list_saved_jobs(self) -> list[dict]:
        rows = self.conn.execute(
            """
            SELECT
              jobs.provider_job_key,
              jobs.company,
              jobs.title,
              jobs.location_raw,
              jobs.url,
              jobs.posted_at,
              jobs.provider,
              job_user_state.state
            FROM jobs
            JOIN job_user_state
              ON jobs.provider_job_key = job_user_state.job_id
            WHERE job_user_state.state IN ('saved', 'applied', 'interview', 'offer')
            ORDER BY job_user_state.updated_at DESC
            """
        ).fetchall()

        jobs: list[dict] = []
        for row in rows:
            jobs.append(
                {
                    "job_id": row[0],
                    "company": row[1],
                    "title": row[2],
                    "location": row[3],
                    "url": row[4],
                    "posted_at": row[5],
                    "provider": row[6],
                    "state": row[7],
                }
            )
        return jobs

    @staticmethod
    def _build_role_ranking_expression(role: Optional[str]) -> tuple[str, list[str]]:
        if not role or not role.strip():
            return "", []

        normalized_role = role.strip().lower()
        tokens = [token for token in normalized_role.split() if token]
        unique_tokens: list[str] = []
        for token in tokens:
            if token not in unique_tokens:
                unique_tokens.append(token)

        parts = ["CASE WHEN LOWER(jobs.title) LIKE ? THEN 10 ELSE 0 END"]
        params: list[str] = [f"%{normalized_role}%"]

        for token in unique_tokens:
            parts.append("CASE WHEN LOWER(jobs.title) LIKE ? THEN 3 ELSE 0 END")
            params.append(f"%{token}%")

        return " + ".join(parts), params

    @staticmethod
    def _experience_tokens(experience: str) -> list[str]:
        mapping = {
            "junior": ["junior", "new grad", "entry"],
            "mid": ["engineer", "developer"],
            "senior": ["senior", "staff", "principal"],
        }
        return mapping.get(experience, [])

    @staticmethod
    def _safe_json_loads(payload: Optional[str]):
        if not payload:
            return None
        try:
            return json.loads(payload)
        except (TypeError, ValueError, json.JSONDecodeError):
            return None

    def _extract_ai_relevance_score(self, raw_provider_payload_json: Optional[str]) -> float:
        payload = self._safe_json_loads(raw_provider_payload_json)
        if not isinstance(payload, dict):
            return 0.0

        score = payload.get("ai_relevance_score")
        if isinstance(score, (int, float)):
            return float(score)

        return 0.0

    def _build_discovery_where_and_params(
        self,
        *,
        location: Optional[str],
        role: Optional[str],
        experience: Optional[str],
        company: Optional[str],
        ai_filter: Optional[str],
        signal: Optional[str],
        signals: Optional[list[str]],
    ) -> tuple[list[str], list]:
        where = ["is_archived = 0"]
        params: list = []

        if location:
            pattern = f"%{location.strip().lower()}%"
            where.append(
                "("
                "LOWER(COALESCE(location_raw, '')) LIKE ? "
                "OR LOWER(COALESCE(location_norm, '')) LIKE ? "
                "OR LOWER(REPLACE(COALESCE(location_norm, ''), '_', ' ')) LIKE ?"
                ")"
            )
            params.extend([pattern, pattern, pattern])

        if role:
            tokens = [t for t in role.strip().lower().split() if t]
            for token in tokens:
                where.append("LOWER(title) LIKE ?")
                params.append(f"%{token}%")

        if company:
            params.append(f"%{company.strip().lower()}%")
            where.append("LOWER(company) LIKE ?")

        if experience:
            exp = experience.strip().lower()
            tokens = self._experience_tokens(exp)
            if tokens:
                clauses = []
                for token in tokens:
                    clauses.append("LOWER(title) LIKE ?")
                    params.append(f"%{token}%")
                where.append("(" + " OR ".join(clauses) + ")")
            else:
                where.append("LOWER(title) LIKE ?")
                params.append(f"%{exp}%")

        if ai_filter and ai_filter.strip().lower() == "ai_only":
            where.append(
                "COALESCE("
                "CASE "
                "WHEN json_valid(raw_provider_payload_json) "
                "THEN CAST(json_extract(raw_provider_payload_json, '$.ai_relevance_score') AS REAL) "
                "ELSE 0 "
                "END, "
                "0"
                ") > 0.0"
            )

        selected_signals: list[str] = []
        if signals:
            selected_signals.extend(
                [s.strip().lower() for s in signals if isinstance(s, str) and s.strip()]
            )
        if signal and signal.strip():
            selected_signals.append(signal.strip().lower())
        selected_signals = list(dict.fromkeys(selected_signals))

        if selected_signals:
            placeholders = ", ".join(["?"] * len(selected_signals))
            where.append(
                "EXISTS ("
                "SELECT 1 "
                "FROM json_each("
                "CASE WHEN json_valid(raw_provider_payload_json) "
                "THEN raw_provider_payload_json "
                "ELSE '{}' END, "
                "'$.signals'"
                ") "
                f"WHERE LOWER(CAST(json_each.value AS TEXT)) IN ({placeholders})"
                ")"
            )
            params.extend(selected_signals)

        return where, params

    def _extract_persisted_signals(
        self,
        *,
        raw_provider_payload_json: Optional[str],
        title: str,
    ) -> list[str]:
        payload = self._safe_json_loads(raw_provider_payload_json)
        if isinstance(payload, dict):
            raw_signals = payload.get("signals")
            if isinstance(raw_signals, list):
                normalized = [
                    str(signal).strip().lower()
                    for signal in raw_signals
                    if str(signal).strip()
                ]
                if normalized:
                    return normalized

        # Backward compatibility for older rows that predate stored title signals.
        return extract_title_signals(title)
