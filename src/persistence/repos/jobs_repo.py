# src/persistence/repos/jobs_repo.py

from sqlite3 import IntegrityError
from typing import Optional
from persistence.models import JobRecord
from persistence.errors import JobNotFoundError


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
    ) -> tuple[list[dict], int]:
        where, params = self._build_discovery_where_and_params(
            location=location,
            role=role,
            experience=experience,
            company=company,
        )

        page = max(1, page)
        page_size = max(1, page_size)
        offset = (page - 1) * page_size

        count_row = self.conn.execute(
            f"""
            SELECT COUNT(*)
            FROM jobs
            WHERE {' AND '.join(where)}
            """,
            tuple(params),
        ).fetchone()
        total_jobs = int(count_row[0]) if count_row else 0

        paged_params = list(params)
        paged_params.extend([page_size, offset])

        rows = self.conn.execute(
            f"""
            SELECT jobs.provider_job_key, jobs.company, jobs.title, jobs.location_raw, jobs.url, jobs.posted_at, jobs.provider, job_user_state.state
            FROM jobs
            LEFT JOIN job_user_state
              ON jobs.provider_job_key = job_user_state.job_id
            WHERE {' AND '.join(where)}
            ORDER BY jobs.discovered_at DESC
            LIMIT ?
            OFFSET ?
            """,
            tuple(paged_params),
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
    def _experience_tokens(experience: str) -> list[str]:
        mapping = {
            "junior": ["junior", "new grad", "entry"],
            "mid": ["engineer", "developer"],
            "senior": ["senior", "staff", "principal"],
        }
        return mapping.get(experience, [])

    def _build_discovery_where_and_params(
        self,
        *,
        location: Optional[str],
        role: Optional[str],
        experience: Optional[str],
        company: Optional[str],
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
            params.append(f"%{role.strip().lower()}%")
            where.append("LOWER(title) LIKE ?")

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

        return where, params
