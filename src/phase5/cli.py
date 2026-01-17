"""
Phase 5 CLI — Guided Job → Evidence Gap Surfacing (read-only)

Usage:
  python -m phase5.cli --job job.txt --resume resume.txt
  python -m phase5.cli gap --job job.txt --resume resume.txt
  python -m phase5.cli proposals
"""

import argparse
from pathlib import Path

from phase5.extract_requirements import extract_requirements
from phase5.match_evidence import match_evidence
from phase5.render_gap_summary import render_gap_summary

def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_gap(args):
    job_text = load_text(Path(args.job))
    resume_text = load_text(Path(args.resume))

    requirements = extract_requirements(job_text)
    matches = match_evidence(requirements, resume_text)
    output_md = render_gap_summary(matches)

    print(output_md)


def run_proposals(args):
    print("\n--- AI Proposals (optional) ---")
    print("No proposals available.")
    print("\n(This system does not generate or apply AI output by default.)")


def main():
    parser = argparse.ArgumentParser(
        description="Phase 5 job ↔ evidence analysis (read-only)"
    )

    subparsers = parser.add_subparsers(dest="command")

    # --- gap subcommand ---
    gap_parser = subparsers.add_parser(
        "gap",
        help="Run deterministic job ↔ resume gap analysis"
    )
    gap_parser.add_argument("--job", required=True, help="Path to job posting text file")
    gap_parser.add_argument("--resume", required=True, help="Path to resume text file")
    gap_parser.set_defaults(func=run_gap)

    # --- proposals subcommand ---
    proposals_parser = subparsers.add_parser(
        "proposals",
        help="List optional AI proposals (requires explicit opt-in)"
    )
    proposals_parser.set_defaults(func=run_proposals)

    # --- backward compatibility ---
    # If no subcommand is provided, assume "gap"
    args, unknown = parser.parse_known_args()

    if args.command is None:
        # Re-parse as gap command
        args = parser.parse_args(["gap"] + unknown)
        args.func = run_gap

    args.func(args)


if __name__ == "__main__":
    main()

