"""
Extract explicit job requirements.

Rules:
- Only extract clearly stated requirements
- No inference
- If ambiguous, mark ambiguous
"""

from typing import List, Dict


def extract_requirements(job_text: str) -> List[Dict]:
    requirements = []

    lines = [l.strip() for l in job_text.splitlines() if l.strip()]

    for line in lines:
        if line.lower().startswith((
            "requirements",
            "qualifications",
            "you will",
            "you have",
            "- ",
            "• "
        )):
            requirements.append({
                "requirement_text": line.lstrip("-• ").strip(),
                "confidence": "explicit"
            })

    return requirements

