"""
Daily Session Runner

This module orchestrates a single user session (e.g. "today").
It does NOT perform intelligence, interpretation, or analysis.

Responsibilities:
- Capture user intent
- Trigger discovery
- Present DAILY_OUTPUT
- Route user interaction to existing adapters

This file is allowed to feel procedural.
It is the conductor, not the engine.
"""

from typing import Optional

# ---- imports from existing system ----

from src.generate_daily_output import generate_daily_output
from src.ui.read_job import read_job_interactive

# (Later)
# from src.state import SessionState


# -------------------------
# Session entrypoint
# -------------------------

def run_daily() -> None:
    """
    Run a single daily session.

    This is the main UX spine:
    intent → discovery → browse → select → interact
    """

    _print_header()

    intent = _capture_intent()
    if intent is None:
        _exit_gracefully()
        return

    _run_discovery(intent)

    while True:
        selection = _prompt_for_job_selection()
        if selection is None:
            _exit_gracefully()
            return

        _handle_job_interaction(selection)


# -------------------------
# UX helpers (thin, boring)
# -------------------------

def _print_header() -> None:
    print("\n=== letsA(ppl)I — Daily Session ===\n")


def _capture_intent() -> Optional[str]:
    """
    Ask the user what kind of role they are exploring today.
    """
    print("What kind of role are you exploring today?")
    print("(e.g. 'iOS engineer', 'AI product', 'demo engineer')")
    print("Press Enter to exit.\n")

    raw = input("> ").strip()
    return raw if raw else None


def _run_discovery(intent: str) -> None:
    """
    Trigger discovery and generate DAILY_OUTPUT.
    """
    print(f"\nDiscovering roles related to: {intent!r}\n")

    # This function already exists and is locked
    print(f"\nDiscovering roles related to: {intent!r}\n")

    markdown, job_id_map = generate_daily_output(intent=intent)

    with open("DAILY_OUTPUT.md", "w") as f:
        f.write(markdown)
    print("\nDaily output generated.")
    print("Open DAILY_OUTPUT.md to browse discovered roles.\n")


def _prompt_for_job_selection() -> Optional[str]:
    """
    Ask the user which job they want to inspect.
    """
    print("Enter a job ID (e.g. stripe:7390314) to view details.")
    print("Press Enter to end your session.\n")

    raw = input("> ").strip()
    return raw if raw else None


def _handle_job_interaction(job_id: str) -> None:
    """
    Route interaction with a specific job.

    This intentionally delegates to UI adapters.
    """
    print(f"\nOpening job: {job_id}\n")

    # This adapter is Phase 5.1–safe
    read_job_interactive(job_id)

    print("\nReturning to job list.\n")


def _exit_gracefully() -> None:
    print("\nSession ended. See you next time.\n")


# -------------------------
# CLI hook
# -------------------------

if __name__ == "__main__":
    run_daily()

