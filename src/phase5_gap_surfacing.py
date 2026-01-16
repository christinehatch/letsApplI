"""
Phase 5.1 — Job → Evidence Gap Surfacing (CLI-first)

Read-only, explainable, no automation.
"""

from pathlib import Path
import argparse


# -------------------------
# Helpers
# -------------------------

def load_text(path: str) -> str:
    """Load and normalize plain text input."""
    return Path(path).read_text().strip()


# -------------------------
# Main logic (stub for now)
# -------------------------

def main(job_path: str, resume_path: str) -> None:
    job_text = load_text(job_path)
    resume_text = load_text(resume_path)

    print("Job text loaded:")
    print(job_text[:300], "...\n")

    print("Resume text loaded:")
    print(resume_text[:300], "...\n")

    print("✅ Phase 5.1 CLI wiring works.")


# -------------------------
# CLI entrypoint
# -------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Surface evidence gaps between a job posting and a resume."
    )
    parser.add_argument("--job", required=True, help="Path to job description text")
    parser.add_argument("--resume", required=True, help="Path to resume text")

    args = parser.parse_args()

    main(args.job, args.resume)
