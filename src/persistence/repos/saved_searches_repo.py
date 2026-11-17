"""Saved searches: the user's own lenses for the Today view."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Optional[str]) -> str:
    return " ".join((value or "").split())


# Short terms people type in lowercase but read as acronyms.
_ACRONYMS = {
    "ai", "ml", "pm", "tpm", "em", "swe", "sre", "ux", "ui", "qa", "llm", "nlp",
    "sf", "nyc", "la", "dc", "uk", "us", "usa", "eu",
}


def _display(text: str) -> str:
    return " ".join(w.upper() if w.lower() in _ACRONYMS else w for w in text.split())


def default_name(role: str, location: str, company: str) -> str:
    parts = [_display(p) for p in (role, company, location) if p]
    if not parts:
        return "All roles"
    label = " · ".join(parts)
    return label[:1].upper() + label[1:]


class SavedSearchesRepo:

    def __init__(self, conn):
        self.conn = conn

    def create(
        self,
        *,
        role: Optional[str] = None,
        location: Optional[str] = None,
        company: Optional[str] = None,
        name: Optional[str] = None,
        include_existing: bool = False,
    ) -> dict:
        role, location, company = _clean(role), _clean(location), _clean(company)
        if not (role or location or company):
            raise ValueError("A saved search needs a keyword, location, or company.")

        now = _now_iso()
        # '' sorts before every ISO timestamp, so all open roles count as new.
        new_since = "" if include_existing else now
        name = _clean(name) or default_name(role, location, company)

        cur = self.conn.execute(
            """
            INSERT INTO saved_searches (name, role, location, company, new_since, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, role, location, company, new_since, now),
        )
        self.conn.commit()
        return self.get(cur.lastrowid)

    def get(self, search_id: int) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT id, name, role, location, company, new_since, created_at FROM saved_searches WHERE id = ?",
            (search_id,),
        ).fetchone()
        return dict(row) if row else None

    def list(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT id, name, role, location, company, new_since, created_at FROM saved_searches ORDER BY id"
        ).fetchall()
        return [dict(r) for r in rows]

    def delete(self, search_id: int) -> bool:
        cur = self.conn.execute("DELETE FROM saved_searches WHERE id = ?", (search_id,))
        self.conn.commit()
        return cur.rowcount > 0
