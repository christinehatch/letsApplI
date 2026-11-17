"""
Milestone 6.3: deterministic recommendations from the user's profile.

No AI runs here. Everything is plain text matching against job metadata
(title, company, location, department), so every recommendation can name
the exact profile entry it came from:

* suggest_searches() turns confirmed roles + location preferences into saved
  searches the user can add to Today.
* reasons() says why a Today item matches the profile.
* hidden_reason() leaves out roles the user's own preferences rule out
  (levels they didn't pick, industries they said to avoid).

Nothing here scores or ranks the person.
"""

from __future__ import annotations

import json
import re
from typing import Iterable, Optional

from discovery.search_query import location_patterns, role_term_patterns, _compiled

SOURCE_LABELS = {
    "resume": "resume",
    "linkedin": "LinkedIn",
    "website": "website",
    "transcript": "transcript",
}

MAX_SUGGESTIONS = 10
MAX_LOCATIONS = 3

# --------------------------------------------------------------------
# Profile
# --------------------------------------------------------------------


def load_profile(conn) -> dict:
    """Only what the user confirmed or typed. Proposed and rejected facts are ignored."""
    facts = conn.execute(
        """
        SELECT f.kind, f.text, s.kind AS source_kind
        FROM profile_facts f
        LEFT JOIN profile_sources s ON s.id = f.source_id
        WHERE f.status = 'confirmed'
        ORDER BY f.id
        """
    ).fetchall()
    prefs: dict[str, list[str]] = {}
    for r in conn.execute("SELECT kind, value FROM profile_preferences ORDER BY id").fetchall():
        prefs.setdefault(r["kind"], []).append(r["value"])

    def label(row) -> str:
        return SOURCE_LABELS.get(row["source_kind"] or "", "your skills")

    return {
        "titles": [(r["text"], label(r)) for r in facts if r["kind"] == "title"],
        "skills": [(r["text"], label(r)) for r in facts if r["kind"] == "skill"],
        "location_facts": [r["text"] for r in facts if r["kind"] == "location"],
        "locations": prefs.get("location", []),
        "work_mode": prefs.get("work_mode", []),
        "levels": prefs.get("level", []),
        "industry_in": prefs.get("industry_in", []),
        "industry_out": prefs.get("industry_out", []),
    }


def is_empty(profile: dict) -> bool:
    return not any(profile.get(k) for k in ("titles", "skills", "locations", "levels", "industry_in", "industry_out"))


# --------------------------------------------------------------------
# Titles
# --------------------------------------------------------------------

_LEVEL_WORDS = r"senior|sr\.?|junior|jr\.?|staff|principal|lead|intern|entry[- ]level|associate"


def core_title(title: str) -> str:
    """
    The role itself, without employer, dates or seniority:
    "Senior Data Engineer at Acme Health (2022-2025)" -> "Data Engineer".
    """
    t = re.sub(r"\(.*?\)", " ", title)
    t = re.split(r"\s+(?:at|@)\s+|\s+[-–—|]\s+|,\s*", t, maxsplit=1)[0]
    t = re.sub(rf"^(?:(?:{_LEVEL_WORDS})\s+)+", "", t.strip(), flags=re.I)
    t = re.sub(r"\s+(?:I{1,3}|IV|[1-4])$", "", t)
    return " ".join(t.split())


def title_level(title: str) -> Optional[str]:
    """The level a job title states outright, or None if it doesn't say."""
    t = title.lower()
    if re.search(r"\bintern(ship)?\b", t):
        return "intern"
    if re.search(r"\b(vp|vice president|chief|head of|director)\b", t):
        return "director"
    if re.search(r"\b(engineering|people|team) manager\b|\bmanager,? (engineering|software)\b", t):
        return "manager"
    if re.search(r"\bprincipal\b|\bdistinguished\b", t):
        return "principal"
    if re.search(r"\bstaff\b", t):
        return "staff"
    if re.search(r"\b(senior|sr\.?)\b|\blead\b|\b(iii|iv)\s*$", t):
        return "senior"
    if re.search(r"\b(junior|jr\.?|new grad(uate)?|entry[- ]level|early[- ]career|apprentice)\b|\b(i|1)\s*$", t):
        return "entry"
    if re.search(r"\b(ii|2)\s*$", t):
        return "mid"
    return None


# --------------------------------------------------------------------
# Matching helpers
# --------------------------------------------------------------------


def _matches(patterns: list[str], text: str) -> bool:
    return bool(patterns) and all(_compiled(p).search(text) for p in patterns)


def _word_in(term: str, text: str) -> bool:
    term = " ".join(term.lower().split())
    if not term:
        return False
    body = r"[\s\-/_.,]+".join(re.escape(w) for w in term.split())
    return re.search(rf"(?<![a-z0-9]){body}(?![a-z0-9])", text.lower()) is not None


def _departments(raw_payload: Optional[str]) -> str:
    try:
        meta = json.loads(raw_payload or "{}")
    except (TypeError, ValueError):
        return ""
    if not isinstance(meta, dict):
        return ""
    parts: list[str] = []
    for key in ("departments", "department", "team"):
        value = meta.get(key)
        if isinstance(value, list):
            parts.extend(str(v) for v in value if v)
        elif value:
            parts.append(str(value))
    return " ".join(parts)


def _locations(profile: dict) -> list[tuple[str, str]]:
    """(place, where it came from), preferences first, then resume places; Remote if wanted."""
    out: list[tuple[str, str]] = []
    if profile.get("locations"):
        out = [(l, "your preferences") for l in profile["locations"]]
    else:
        # Places from the resume, city only ("San Jose, CA" -> "San Jose").
        out = [(l.split(",")[0].strip(), "your resume") for l in profile.get("location_facts") or [] if l.strip()]
    if "remote" in (profile.get("work_mode") or []) and not any("remote" in l.lower() for l, _ in out):
        out.append(("Remote", "your preferences"))
    deduped: list[tuple[str, str]] = []
    for loc, src in out:
        if loc and loc.lower() not in {d.lower() for d, _ in deduped}:
            deduped.append((loc, src))
    return deduped[:MAX_LOCATIONS]


# --------------------------------------------------------------------
# Suggested searches
# --------------------------------------------------------------------


def suggest_searches(profile: dict, count_open, existing: Iterable[dict]) -> list[dict]:
    """
    One suggestion per (role you've held, place you want to work) that matches
    open roles right now. `count_open(search) -> int` is supplied by the caller.
    Roles with no open matches aren't suggested.
    """
    taken = {((s.get("role") or "").lower(), (s.get("location") or "").lower()) for s in existing}
    locations = _locations(profile) or [("", "")]
    seen_titles: set[str] = set()
    out: list[dict] = []

    for title, source in profile.get("titles") or []:
        core = core_title(title)
        key = core.lower()
        if not core or key in seen_titles:
            continue
        seen_titles.add(key)
        for loc, loc_source in locations:
            if (key, loc.lower()) in taken:
                continue
            search = {"role": key, "location": loc, "company": "", "new_since": ""}
            open_count = count_open(search)
            if open_count <= 0:
                continue
            why = [f"{core} (your {source})"]
            if loc:
                why.append(f"{loc} ({loc_source})")
            out.append({
                "name": f"{core} · {loc}" if loc else core,
                "role": key,
                "location": loc,
                "open_count": open_count,
                "why": why,
            })
            if len(out) >= MAX_SUGGESTIONS:
                return out
    return out


# --------------------------------------------------------------------
# Today: why an item showed up, and what preferences hide
# --------------------------------------------------------------------


def reasons(item: dict, profile: dict) -> list[str]:
    """Profile entries this role matches, each with where it came from."""
    title = item.get("title") or ""
    places = " ; ".join(item.get("locations") or [])
    out: list[str] = []

    for t, source in profile.get("titles") or []:
        core = core_title(t)
        if core and _matches(role_term_patterns(core), title):
            out.append(f"{core} (your {source})")
            break

    skill_hits = [
        f"{skill} ({source if source == 'your skills' else 'your ' + source})"
        for skill, source in profile.get("skills") or []
        if _word_in(skill, title)
    ]
    out.extend(skill_hits[:3])

    for loc in profile.get("locations") or []:
        if _matches(location_patterns(loc), places):
            out.append(f"{loc} (your preferences)")
            break

    level = title_level(title)
    if level and level in (profile.get("levels") or []):
        out.append(f"{level.capitalize()} level (your preferences)")

    text = f"{title} {item.get('company') or ''} {_departments(item.get('_payload'))}"
    for term in profile.get("industry_in") or []:
        if _word_in(term, text):
            out.append(f"{term} (your preferences)")
            break

    # De-duplicate, keep order.
    return list(dict.fromkeys(out))


def hidden_reason(item: dict, profile: dict) -> Optional[tuple[str, str]]:
    """
    (kind, detail) if the user's own preferences rule this role out, else None.
    Only acts on what the title or company plainly says.
    """
    levels = profile.get("levels") or []
    if levels:
        level = title_level(item.get("title") or "")
        if level and level not in levels:
            return ("level", level)

    text = f"{item.get('title') or ''} {item.get('company') or ''} {_departments(item.get('_payload'))}"
    for term in profile.get("industry_out") or []:
        if _word_in(term, text):
            return ("industry", term)
    return None
