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
from phase5.mock_proposals import get_mock_proposals

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
    proposals = get_mock_proposals()

    if not proposals:
        print("\n--- AI Proposals (optional) ---")
        print("No proposals available.")
        print("\n(This system does not generate or apply AI output by default.)")
        return

    # List proposals
    if args.action is None:
        print("\n--- AI Proposals (optional) ---")
        for i, p in enumerate(proposals, start=1):
            print(f"[{i}] {p.context} ({p.status})")
        return

    index = args.proposal_id - 1
    if index < 0 or index >= len(proposals):
        print("Invalid proposal id.")
        return

    p = proposals[index]

    # Show proposal
    if args.action == "show":
        print("\n⚠️  AI-generated content (not authoritative)")
        print(f"Context: {p.context}")
        print(f"Generated at: {p.generated_at}")
        print("\n--------------------------------")
        print(p.text)
        print("--------------------------------")
        return

    # Accept proposal
    if args.action == "accept":
        p.status = "accepted"
        print("\n✓ Proposal accepted (ephemeral)")
        print("\n--- User-authored content ---")
        print(p.text)
        print("-----------------------------")
        return

    # Edit proposal
    if args.action == "edit":
        print("\nEnter your edited version below.")
        print("Finish with Ctrl+D (Unix) or Ctrl+Z + Enter (Windows):\n")

        try:
            edited_text = input()
        except EOFError:
            edited_text = ""

        p.status = "edited"
        print("\n✓ Proposal edited and accepted (ephemeral)")
        print("\n--- User-authored content ---")
        print(edited_text)
        print("-----------------------------")
        return

    # Reject proposal
    if args.action == "reject":
        p.status = "rejected"
        print("\n✗ Proposal rejected.")
        print("(No changes were applied.)")
        return


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

    proposals_subparsers = proposals_parser.add_subparsers(dest="action")
    accept_parser = proposals_subparsers.add_parser(
        "accept",
        help="Accept an AI proposal as-is (ephemeral)"
    )
    accept_parser.add_argument("proposal_id", type=int)

    edit_parser = proposals_subparsers.add_parser(
        "edit",
        help="Edit an AI proposal before accepting (ephemeral)"
    )
    edit_parser.add_argument("proposal_id", type=int)

    reject_parser = proposals_subparsers.add_parser(
        "reject",
        help="Reject an AI proposal (ephemeral)"
    )
    reject_parser.add_argument("proposal_id", type=int)

    show_parser = proposals_subparsers.add_parser(
        "show",
        help="Show an AI proposal by id (read-only)"
    )
    show_parser.add_argument(
        "proposal_id",
        type=int,
        help="Proposal id to show"
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

