"""The user's profile: sources they added, facts, and work preferences (Milestone 6.1)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Optional

SOURCE_KINDS = ("resume", "linkedin", "website", "transcript")
PREFERENCE_KINDS = ("location", "work_mode", "level", "company_size", "industry_in", "industry_out")

# Fixed choices; free-text kinds (location, industry_*) accept anything.
PREFERENCE_CHOICES = {
    "work_mode": ("remote", "hybrid", "onsite"),
    "level": ("intern", "entry", "mid", "senior", "staff", "principal", "manager", "director"),
    "company_size": ("startup", "small", "mid", "large"),
}

MAX_PREFERENCE_VALUE = 80
MAX_SKILL = 60
MAX_SKILLS = 200


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: object) -> str:
    return " ".join(str(value or "").split())


def _dedupe(values: Iterable[object], *, limit: int, max_len: int) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for v in values:
        text = _clean(v)[:max_len]
        key = text.lower()
        if text and key not in seen:
            seen.add(key)
            out.append(text)
        if len(out) >= limit:
            break
    return out


class ProfileRepo:

    def __init__(self, conn):
        self.conn = conn

    # ------------------------------------------------------------
    # Sources
    # ------------------------------------------------------------

    def add_source(
        self,
        *,
        kind: str,
        label: str,
        file_path: Optional[str] = None,
        url: Optional[str] = None,
        extracted_text: Optional[str] = None,
    ) -> dict:
        if kind not in SOURCE_KINDS:
            raise ValueError(f"Unknown source kind: {kind}")
        if not file_path and not url:
            raise ValueError("A source needs a file or a link.")
        cur = self.conn.execute(
            """
            INSERT INTO profile_sources (kind, label, file_path, url, extracted_text, added_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (kind, _clean(label) or kind, file_path, url, extracted_text, _now()),
        )
        self.conn.commit()
        return self.get_source(cur.lastrowid)

    def get_source(self, source_id: int, *, with_text: bool = False) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM profile_sources WHERE id = ?", (source_id,)
        ).fetchone()
        return self._source_dict(row, with_text=with_text) if row else None

    def list_sources(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM profile_sources ORDER BY added_at DESC, id DESC"
        ).fetchall()
        return [self._source_dict(r) for r in rows]

    def delete_source(self, source_id: int) -> Optional[dict]:
        """Delete the row and its facts. Returns the deleted source so the caller can remove its file."""
        source = self.get_source(source_id)
        if source is None:
            return None
        self.conn.execute("DELETE FROM profile_facts WHERE source_id = ?", (source_id,))
        self.conn.execute("DELETE FROM profile_sources WHERE id = ?", (source_id,))
        self.conn.commit()
        return source

    @staticmethod
    def _source_dict(row, *, with_text: bool = False) -> dict:
        text = row["extracted_text"] or ""
        out = {
            "id": row["id"],
            "kind": row["kind"],
            "label": row["label"],
            "url": row["url"],
            "has_file": bool(row["file_path"]),
            "file_path": row["file_path"],
            "added_at": row["added_at"],
            "read_at": row["read_at"],
            "text_chars": len(text),
            "text_preview": " ".join(text.split())[:240],
        }
        if with_text:
            out["text"] = text
        return out

    # ------------------------------------------------------------
    # Typed skills (facts with no source, confirmed by definition)
    # ------------------------------------------------------------

    def list_skills(self) -> list[str]:
        rows = self.conn.execute(
            """
            SELECT text FROM profile_facts
            WHERE source_id IS NULL AND kind = 'skill' AND status = 'confirmed'
            ORDER BY id
            """
        ).fetchall()
        return [r["text"] for r in rows]

    def set_skills(self, skills: Iterable[object]) -> list[str]:
        cleaned = _dedupe(skills, limit=MAX_SKILLS, max_len=MAX_SKILL)
        now = _now()
        self.conn.execute(
            "DELETE FROM profile_facts WHERE source_id IS NULL AND kind = 'skill'"
        )
        self.conn.executemany(
            """
            INSERT INTO profile_facts (source_id, kind, text, status, created_at, updated_at)
            VALUES (NULL, 'skill', ?, 'confirmed', ?, ?)
            """,
            [(s, now, now) for s in cleaned],
        )
        self.conn.commit()
        return cleaned

    # ------------------------------------------------------------
    # Preferences
    # ------------------------------------------------------------

    def get_preferences(self) -> dict[str, list[str]]:
        prefs: dict[str, list[str]] = {k: [] for k in PREFERENCE_KINDS}
        for r in self.conn.execute(
            "SELECT kind, value FROM profile_preferences ORDER BY id"
        ).fetchall():
            prefs[r["kind"]].append(r["value"])
        return prefs

    def set_preferences(self, prefs: dict) -> dict[str, list[str]]:
        unknown = set(prefs) - set(PREFERENCE_KINDS)
        if unknown:
            raise ValueError(f"Unknown preference: {sorted(unknown)[0]}")

        rows: list[tuple[str, str]] = []
        for kind in PREFERENCE_KINDS:
            values = _dedupe(prefs.get(kind) or [], limit=50, max_len=MAX_PREFERENCE_VALUE)
            allowed = PREFERENCE_CHOICES.get(kind)
            if allowed:
                values = [v.lower() for v in values]
                bad = [v for v in values if v not in allowed]
                if bad:
                    raise ValueError(f"'{bad[0]}' isn't a choice for {kind.replace('_', ' ')}.")
            rows.extend((kind, v) for v in values)

        now = _now()
        self.conn.execute("DELETE FROM profile_preferences")
        self.conn.executemany(
            "INSERT INTO profile_preferences (kind, value, updated_at) VALUES (?, ?, ?)",
            [(k, v, now) for k, v in rows],
        )
        self.conn.commit()
        return self.get_preferences()

    # ------------------------------------------------------------
    # Facts read from a source (6.2): proposed → confirmed / rejected
    # ------------------------------------------------------------

    def set_source_text(self, source_id: int, text: str) -> None:
        self.conn.execute(
            "UPDATE profile_sources SET extracted_text = ? WHERE id = ?", (text, source_id)
        )
        self.conn.commit()

    def replace_proposals(self, source_id: int, facts: list[dict]) -> int:
        """
        Swap this source's pending proposals for a new reading. Facts the user
        already confirmed or rejected stay as they were and aren't proposed again.
        Returns how many new proposals were added.
        """
        now = _now()
        self.conn.execute(
            "DELETE FROM profile_facts WHERE source_id = ? AND status = 'proposed'", (source_id,)
        )
        decided = {
            (r["kind"], r["text"].lower())
            for r in self.conn.execute(
                "SELECT kind, text FROM profile_facts WHERE source_id = ?", (source_id,)
            ).fetchall()
        }
        rows = [
            (source_id, f["kind"], f["text"], f["quote"], now, now)
            for f in facts
            if (f["kind"], f["text"].lower()) not in decided
        ]
        self.conn.executemany(
            """
            INSERT INTO profile_facts (source_id, kind, text, quote, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'proposed', ?, ?)
            """,
            rows,
        )
        self.conn.execute("UPDATE profile_sources SET read_at = ? WHERE id = ?", (now, source_id))
        self.conn.commit()
        return len(rows)

    def list_source_facts(self) -> list[dict]:
        """Every fact read from a source, except ones the user rejected."""
        rows = self.conn.execute(
            """
            SELECT id, source_id, kind, text, quote, status, updated_at
            FROM profile_facts
            WHERE source_id IS NOT NULL AND status != 'rejected'
            ORDER BY source_id, id
            """
        ).fetchall()
        return [dict(r) for r in rows]

    def get_fact(self, fact_id: int) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT id, source_id, kind, text, quote, status, updated_at FROM profile_facts WHERE id = ?",
            (fact_id,),
        ).fetchone()
        return dict(row) if row else None

    def update_fact(self, fact_id: int, *, status: Optional[str] = None, text: Optional[str] = None) -> Optional[dict]:
        fact = self.get_fact(fact_id)
        if fact is None or fact["source_id"] is None:
            return None
        if status is not None and status not in ("confirmed", "rejected", "proposed"):
            raise ValueError("Unknown status.")
        new_text = fact["text"] if text is None else _clean(text)[:MAX_SKILL * 2]
        if not new_text:
            raise ValueError("A fact can't be empty.")
        self.conn.execute(
            "UPDATE profile_facts SET status = ?, text = ?, updated_at = ? WHERE id = ?",
            (status or fact["status"], new_text, _now(), fact_id),
        )
        self.conn.commit()
        return self.get_fact(fact_id)

    def confirm_all(self, source_id: int) -> int:
        cur = self.conn.execute(
            "UPDATE profile_facts SET status = 'confirmed', updated_at = ? WHERE source_id = ? AND status = 'proposed'",
            (_now(), source_id),
        )
        self.conn.commit()
        return cur.rowcount
