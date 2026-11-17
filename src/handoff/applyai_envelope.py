"""
letsA(ppl)I → applyAI role handoff envelope (v1.0).

Contract: docs/APPLYAI_HANDOFF_CONTRACT.md §3.

Pure functions only. The envelope is built from an already-validated,
stored Phase 5.2 interpretation; nothing here calls an LLM, reads the
network, or writes anything.

What is deliberately NOT included (§3.3): raw job content, implicit
signals, pipeline state, discovery signals, resume or gap data, user
identifiers. The builder copies an explicit allowlist, so new fields in
the interpretation never leak by default.
"""

from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional

HANDOFF_VERSION = "1.0"
SUPPORTED_INTERPRETATION_SCHEMA = "5.2.0"
FRAMING = "This describes what one job posting says. It says nothing about you."

MAX_QUOTE_CHARS = 500
MAX_ENVELOPE_BYTES = 64 * 1024

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
# Spans are fixed-size chunks of the raw posting, which may be HTML, so a
# chunk can start or end inside a tag: 'start-pos="1337">What…' or '…<p data-r'.
_CUT_TAG_AT_START_RE = re.compile(
    r'^(?:'
    r'[^\s<>"]*="[^"]*"(?:\s+[^\s<>"=]+(?:="[^"]*")?)*'  # attribute residue: os="2533"
    r'|[^\s<>"]*"'                                        # end of a value: 1337"
    r'|/?[\w-]*'                                          # end of a tag name: p, /p
    r')\s*/?>'
)
_CUT_TAG_AT_END_RE = re.compile(r"<[^>]*$")


class EnvelopeBuildError(ValueError):
    """The stored interpretation can't be turned into a valid envelope."""


def _plain_quote(text: str) -> str:
    """Span text may be HTML (description_html). applyAI shows plain text."""
    text = _CUT_TAG_AT_END_RE.sub(" ", _CUT_TAG_AT_START_RE.sub(" ", text))
    plain = _WS_RE.sub(" ", html.unescape(_TAG_RE.sub(" ", text))).strip()
    if len(plain) > MAX_QUOTE_CHARS:
        plain = plain[: MAX_QUOTE_CHARS - 1].rstrip() + "…"
    return plain


def _resolve_evidence(span_ids: Any, span_map: Mapping[str, str], where: str) -> List[str]:
    if not isinstance(span_ids, list) or not span_ids:
        raise EnvelopeBuildError(f"{where} has no evidence spans")
    quotes = []
    for span_id in span_ids:
        text = span_map.get(span_id)
        if not isinstance(text, str) or not text.strip():
            raise EnvelopeBuildError(f"{where} references a missing span: {span_id}")
        quote = _plain_quote(text)
        if not quote:
            raise EnvelopeBuildError(f"{where} references an empty span: {span_id}")
        quotes.append(quote)
    return quotes


def _iso_utc(value: Any) -> str:
    """SQLite CURRENT_TIMESTAMP ('YYYY-MM-DD HH:MM:SS', UTC) or ISO → ISO-8601 Z."""
    if not isinstance(value, str) or not value.strip():
        raise EnvelopeBuildError("Interpretation has no timestamp")
    try:
        dt = datetime.fromisoformat(value.strip().replace(" ", "T").replace("Z", "+00:00"))
    except ValueError:
        raise EnvelopeBuildError(f"Interpretation timestamp is unreadable: {value}")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_applyai_envelope(
    *,
    job_id: str,
    company: str,
    title: str,
    job_url: str,
    interpretation: Mapping[str, Any],
    span_map: Optional[Mapping[str, str]],
    interpreted_at: str,
) -> Dict[str, Any]:
    """
    Build the v1.0 envelope, minus `handoff_id` (the UI adds it at confirm
    time, per contract §3.1). Raises EnvelopeBuildError on any gap.
    """
    if not isinstance(interpretation, Mapping):
        raise EnvelopeBuildError("No interpretation")
    if interpretation.get("schema_version") != SUPPORTED_INTERPRETATION_SCHEMA:
        raise EnvelopeBuildError(
            f"Unsupported interpretation schema: {interpretation.get('schema_version')!r}"
        )
    if not isinstance(job_url, str) or not job_url.startswith("https://"):
        raise EnvelopeBuildError("Job URL is not an https:// link")

    span_map = span_map or {}

    summary = (interpretation.get("RoleSummary") or {}).get("summary_text")
    if not isinstance(summary, str) or not summary.strip():
        raise EnvelopeBuildError("Interpretation has no role summary")

    requirements = [
        {"requirement_text": r["requirement_text"], "modality": r["modality"]}
        for r in (interpretation.get("RequirementsAnalysis") or {}).get("explicit_requirements") or []
    ]

    capabilities = [
        {
            "domain_label": c["domain_label"],
            "description": c["description"],
            "evidence": _resolve_evidence(
                c.get("evidence_span_ids"), span_map, f"Capability {c.get('domain_label')!r}"
            ),
        }
        for c in interpretation.get("CapabilityEmphasisSignals") or []
    ]
    if not capabilities:
        raise EnvelopeBuildError("Interpretation has no capability signals")

    projects = [
        {
            "capability_surface": p["capability_surface"],
            "description": p["description"],
            "evidence": _resolve_evidence(
                p.get("evidence_span_ids"), span_map, f"Project {p.get('capability_surface')!r}"
            ),
        }
        for p in interpretation.get("ProjectOpportunitySignals") or []
    ]

    structural_notes = (interpretation.get("InterpretationResult") or {}).get("structural_notes")
    if not isinstance(structural_notes, str) or not structural_notes.strip():
        raise EnvelopeBuildError("Interpretation has no structural notes")

    envelope = {
        "handoff_version": HANDOFF_VERSION,
        "source": {
            "system": "letsappli",
            "job_id": job_id,
            "company": company,
            "title": title,
            "job_url": job_url,
            "interpretation_schema_version": SUPPORTED_INTERPRETATION_SCHEMA,
            "interpreted_at": _iso_utc(interpreted_at),
        },
        "role": {
            "summary_text": summary,
            "explicit_requirements": requirements,
            "capability_emphasis": capabilities,
            "project_opportunities": projects,
            "structural_notes": structural_notes,
            "confidence": interpretation.get("confidence"),
        },
        "framing": FRAMING,
    }

    # Leave room for the UI-added handoff_id (a UUID).
    if len(json.dumps(envelope).encode("utf-8")) > MAX_ENVELOPE_BYTES - 128:
        raise EnvelopeBuildError("Envelope would be larger than 64 KB")

    return envelope
