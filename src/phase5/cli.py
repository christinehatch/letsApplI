"""
Phase 5.1 CLI — Guided Job → Evidence Gap Surfacing (read-only)

Usage:
  python -m phase5.cli --job job.txt --resume resume.txt
"""

import argparse
from pathlib import Path

from phase5.extract_requirements import extract_requirements
from phase5.match_evidence import match_evidence
from phase5.render_gap_summary import render_gap_summary


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Phase 5.1 gap surfacing (read-only)")
    parser.add_argument("--job", required=True, help="Path to job posting text file")
    parser.add_argument("--resume", required=True, help="Path to resume text file")

    args = parser.parse_args()

    job_text = load_text(Path(args.job))
    resume_text = load_text(Path(args.resume))

    requirements = extract_requirements(job_text)
    matches = match_evidence(requirements, resume_text)
    output_md = render_gap_summary(matches)

    print(output_md)


if __name__ == "__main__":
    main()

