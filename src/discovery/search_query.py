"""
Feed search: turns what the user typed into deterministic match patterns.

Rules
-----
* A query is split into **term groups**. A job must match **every** group.
* A group may have **alternatives** (synonyms). A job needs to match **any**
  one of them. ("ai" → "ai" OR "artificial intelligence"; synonyms widen a
  search, they never narrow it.)
* Terms match at the **start of a word**, so "engineer" matches "Engineering"
  but "pm" doesn't match "Development".
* Short terms (≤ 3 characters, e.g. ai, ml, pm, ux, sf) must match a **whole
  word**, so "ai" doesn't match "Aiven" and "la" doesn't match "Lake".
* Multi-word phrases allow spaces, hyphens, or slashes between words
  ("front end" matches "Front-End").

Patterns are Python regular expressions, evaluated in SQLite through the
REGEXP function registered by `register_regexp`.
"""

from __future__ import annotations

import re
import sqlite3
from functools import lru_cache
from typing import Iterable, List, Optional, Sequence

# Each set is a family of equivalent phrases. Lowercase, single spaces.
ROLE_SYNONYMS: Sequence[Sequence[str]] = (
    ("ai", "artificial intelligence"),
    ("ml", "machine learning"),
    ("pm", "product manager", "product management"),
    ("tpm", "technical program manager"),
    ("em", "engineering manager"),
    ("swe", "software engineer", "software developer"),
    ("sre", "site reliability"),
    ("ux", "user experience"),
    ("ui", "user interface"),
    ("qa", "quality assurance"),
    ("frontend", "front end"),
    ("backend", "back end"),
    ("fullstack", "full stack"),
    ("devops", "dev ops"),
    ("nlp", "natural language processing"),
    ("llm", "large language model"),
)

LOCATION_SYNONYMS: Sequence[Sequence[str]] = (
    ("sf", "san francisco", "bay area", "sfo"),
    ("nyc", "new york"),
    ("la", "los angeles"),
    ("dc", "washington dc", "washington d c"),
    ("uk", "united kingdom"),
    ("us", "usa", "united states"),
)

_SHORT_TERM_MAX = 3
_TOKEN_RE = re.compile(r"[a-z0-9+#]+")


def _tokens(text: str) -> List[str]:
    return _TOKEN_RE.findall(text.lower())


def _phrase_pattern(phrase: str) -> str:
    """Regex for one phrase, anchored at a word start."""
    words = phrase.split()
    body = r"[\s\-/_.,]+".join(re.escape(w) for w in words)
    pattern = rf"(?<![a-z0-9]){body}"
    if len(phrase.replace(" ", "")) <= _SHORT_TERM_MAX:
        pattern += r"(?![a-z0-9])"
    return pattern


def _group_pattern(alternatives: Iterable[str]) -> str:
    return "(?:" + "|".join(_phrase_pattern(a) for a in alternatives) + ")"


def _parse(text: Optional[str], synonym_families: Sequence[Sequence[str]]) -> List[str]:
    """Split text into term groups and return one regex per group."""
    if not text:
        return []
    tokens = _tokens(text)
    if not tokens:
        return []

    # Phrase → its family, longest phrases first for greedy matching.
    lookup = {}
    for family in synonym_families:
        for phrase in family:
            lookup[tuple(phrase.split())] = family
    max_len = max((len(k) for k in lookup), default=1)

    groups: List[str] = []
    i = 0
    while i < len(tokens):
        matched = False
        for size in range(min(max_len, len(tokens) - i), 0, -1):
            key = tuple(tokens[i : i + size])
            family = lookup.get(key)
            if family:
                groups.append(_group_pattern(family))
                i += size
                matched = True
                break
        if not matched:
            groups.append(_group_pattern([tokens[i]]))
            i += 1

    # Same group twice adds nothing.
    return list(dict.fromkeys(groups))


def role_term_patterns(role: Optional[str]) -> List[str]:
    """One regex per term group for a role / keyword search."""
    return _parse(role, ROLE_SYNONYMS)


def location_patterns(location: Optional[str]) -> List[str]:
    """
    One regex per term group for a location filter.

    Location text is also compared with underscores turned into spaces, since
    `location_norm` stores values like 'san_francisco_bay_area'.
    """
    return _parse(location, LOCATION_SYNONYMS)


@lru_cache(maxsize=512)
def _compiled(pattern: str) -> "re.Pattern[str]":
    return re.compile(pattern, re.IGNORECASE)


def _regexp(pattern: Optional[str], value: Optional[str]) -> int:
    if pattern is None or value is None:
        return 0
    return 1 if _compiled(pattern).search(value) else 0


def register_regexp(conn: sqlite3.Connection) -> None:
    """Make `value REGEXP pattern` available on this connection."""
    conn.create_function("REGEXP", 2, _regexp, deterministic=True)
