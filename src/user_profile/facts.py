"""
Milestone 6.2: propose profile facts from one source the user chose to read.

The model only *proposes*. Its output is untrusted: every fact must quote
text that is really in the source, use an allowed kind, and avoid
evaluative language the source doesn't use. Anything else is dropped.
Nothing proposed here enters the profile until the user confirms it.
"""

from __future__ import annotations

import re
from typing import Any, Callable, Optional

FACT_KINDS = ("title", "skill", "domain", "education", "location", "achievement")

MAX_SOURCE_CHARS = 30_000
MAX_FACTS = 60
MAX_TEXT = 120
MAX_QUOTE = 300

# Words that judge the person. Allowed in a fact only if the source itself uses them.
EVALUATIVE_WORDS = {
    "excellent", "exceptional", "outstanding", "impressive", "talented", "brilliant",
    "strong", "expert", "world-class", "skilled", "highly", "passionate", "proven",
    "qualified", "ideal", "best", "great", "top", "rockstar", "ninja",
}

# Advice or fit language is never allowed, whatever the source says.
BANNED_PHRASES = ("you should", "recommend", "good fit", "strong fit", "candidate", "suited for")

# Grades stay out of the profile (docs/PROFILE_PLAN.md §9.1).
_GRADE = re.compile(r"\bgpa\b|\bgrade\b|\b[0-4]\.\d{1,2}\s*/\s*4(\.0+)?\b|\(\s*[A-F][+-]?\s*\)|:\s*[A-F][+-]?\b", re.I)

SOURCE_LABELS = {
    "resume": "a resume",
    "linkedin": "a LinkedIn profile saved as PDF",
    "website": "a personal website",
    "transcript": "an academic transcript",
}


class FactReadError(Exception):
    """Reading failed; the message is safe to show the user."""


def _norm(text: str) -> str:
    return " ".join(str(text).split()).lower()


def system_prompt() -> str:
    return (
        "You extract plain facts about a person from a document they wrote or own.\n"
        "Return JSON only, in this shape:\n"
        '{"facts": [{"kind": "...", "text": "...", "quote": "..."}]}\n\n'
        "kind is one of:\n"
        "- title: a role or job title held, with employer and years if given\n"
        "- skill: a skill, tool, language, framework or method\n"
        "- domain: a field or industry worked in (e.g. payments, health tech)\n"
        "- education: a degree, school, or notable course (never grades or GPA)\n"
        "- location: a place lived or worked\n"
        "- achievement: one specific thing they did, in their words\n\n"
        "Rules:\n"
        "- quote must be copied exactly, character for character, from the document.\n"
        "- text is a short label (under 120 characters) for the fact.\n"
        "- One skill per fact. Do not merge facts.\n"
        "- Only include what the document says. Do not infer, guess or generalize.\n"
        "- Do not describe the person (no 'strong', 'expert', 'talented').\n"
        "- Do not give advice or mention jobs they might want.\n"
        "- Never include grades, GPA, test scores, age, or contact details.\n"
        f"- At most {MAX_FACTS} facts."
    )


def user_prompt(text: str, source_kind: str) -> str:
    label = SOURCE_LABELS.get(source_kind, "a document")
    return f"The document is {label}.\n\n<document>\n{text[:MAX_SOURCE_CHARS]}\n</document>"


def validate_facts(raw: Any, source_text: str) -> tuple[list[dict], list[str]]:
    """
    Keep only facts that pass every rule. Returns (facts, reasons_dropped).
    Raises FactReadError if the output isn't the expected shape at all.
    """
    if not isinstance(raw, dict) or not isinstance(raw.get("facts"), list):
        raise FactReadError("The reader returned something unexpected. Try again.")

    haystack = _norm(source_text)
    kept: list[dict] = []
    dropped: list[str] = []
    seen: set[tuple[str, str]] = set()

    for item in raw["facts"][: MAX_FACTS * 2]:
        if not isinstance(item, dict):
            dropped.append("not an object")
            continue
        kind = str(item.get("kind") or "").strip().lower()
        text = " ".join(str(item.get("text") or "").split())
        quote = " ".join(str(item.get("quote") or "").split())

        if kind not in FACT_KINDS:
            dropped.append(f"unknown kind: {kind or '(none)'}")
            continue
        if not text or len(text) > MAX_TEXT:
            dropped.append("missing or overlong text")
            continue
        if not quote or len(quote) > MAX_QUOTE:
            dropped.append("missing or overlong quote")
            continue
        if _norm(quote) not in haystack:
            dropped.append(f"quote not in source: {quote[:40]}")
            continue

        lowered = text.lower()
        if any(p in lowered for p in BANNED_PHRASES):
            dropped.append(f"advice or fit language: {text[:40]}")
            continue
        quote_words = set(re.findall(r"[a-z][a-z-]*", quote.lower()))
        judged = [w for w in re.findall(r"[a-z][a-z-]*", lowered) if w in EVALUATIVE_WORDS and w not in quote_words]
        if judged:
            dropped.append(f"evaluative word not in source: {judged[0]}")
            continue
        if kind == "education" and (_GRADE.search(text) or _GRADE.search(quote)):
            dropped.append("grades are not kept")
            continue

        key = (kind, lowered)
        if key in seen:
            continue
        seen.add(key)
        kept.append({"kind": kind, "text": text, "quote": quote})
        if len(kept) >= MAX_FACTS:
            break

    return kept, dropped


def propose_facts(
    source_text: str,
    source_kind: str,
    generate: Callable[..., dict],
) -> tuple[list[dict], list[str]]:
    """
    Ask the model for facts and validate them. `generate` is
    LLMAdapter.generate_structured (injected so tests never call the network).
    One retry if the output's shape is wrong; individual bad facts are just dropped.
    """
    if not source_text.strip():
        raise FactReadError("There's no text to read in this source.")

    last_error: Optional[FactReadError] = None
    for _ in range(2):
        try:
            raw = generate(
                system_prompt=system_prompt(),
                user_prompt=user_prompt(source_text, source_kind),
                temperature=0.0,
                max_tokens=3000,
            )
        except Exception as e:  # network, auth, bad JSON
            last_error = FactReadError(_friendly(e))
            continue
        try:
            return validate_facts(raw, source_text)
        except FactReadError as e:
            last_error = e
    raise last_error or FactReadError("Couldn't read this source. Try again.")


def _friendly(error: Exception) -> str:
    message = str(error)
    if "OPENAI_API_KEY" in message:
        return "Reading needs an OpenAI API key. Set OPENAI_API_KEY and restart the API server."
    if "valid JSON" in message:
        return "The reader returned something unexpected. Try again."
    return "Couldn't reach the AI service. Check your connection and try again."
