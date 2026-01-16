"""
Render evidence highlights and gaps as markdown.

Tone rules:
- Neutral
- Observational
- No advice or scoring
"""

from typing import List, Dict


def render_gap_summary(matches: List[Dict]) -> str:
    lines = [
        "# Evidence Visibility Report",
        "",
        "_This report shows what is visible and what is missing based on explicit text only._",
        "",
    ]

    visible = [m for m in matches if m["status"] == "evidence_found"]
    missing = [m for m in matches if m["status"] == "evidence_missing"]

    if visible:
        lines.extend([
            "## ✅ Visible Evidence",
            "",
            "_These requirements are explicitly reflected in your resume._",
            "",
        ])

        for m in visible:
            lines.extend([
                f"### {m['requirement']}",
                "",
                "**Resume evidence:**",
                f"> {m['evidence']}",
                "",
            ])

    if missing:
        lines.extend([
            "## ⚠️ Evidence Not Visible",
            "",
            "_These requirements appear in the job posting, but are not explicitly visible in your resume._",
            "",
        ])

        for m in missing:
            lines.extend([
                f"### {m['requirement']}",
                "",
                "No direct resume evidence was found.",
                "",
                "_You may already have this experience — it just isn’t visible here._",
                "",
            ])

    if not visible and not missing:
        lines.append("_No explicit requirements detected._")

    return "\n".join(lines)
