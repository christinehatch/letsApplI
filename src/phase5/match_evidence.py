"""
Match resume evidence to explicit requirements.

Rules:
- Exact or near-exact textual overlap only
- Capture the matching resume line
- No inference
"""

from typing import List, Dict


def match_evidence(requirements: List[Dict], resume_text: str) -> List[Dict]:
    resume_lines = [l.strip() for l in resume_text.splitlines() if l.strip()]
    results = []

    for req in requirements:
        req_text = req["requirement_text"].lower()
        matched_line = None

        for line in resume_lines:
            if req_text in line.lower():
                matched_line = line
                break

        results.append({
            "requirement": req["requirement_text"],
            "status": "evidence_found" if matched_line else "evidence_missing",
            "evidence": matched_line,
        })

    return results
