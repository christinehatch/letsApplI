import subprocess
from pathlib import Path
import tempfile
import sys

PYTHON = sys.executable
CLI = ["-m", "phase5.cli"]
ENV = {"PYTHONPATH": "src"}


def run_cli(args, input_text=None):
    return subprocess.run(
        [PYTHON, *CLI, *args],
        input=input_text,
        text=True,
        capture_output=True,
        env=ENV,
    )


def test_apply_requires_approval():
    """Invariant: apply cannot occur without prior approval."""
    result = run_cli(["proposals", "edit", "1", "--output", "out.txt"])
    assert "Cannot apply" not in result.stdout
    assert not Path("out.txt").exists()


def test_edit_apply_writes_file():
    """Invariant: edit + apply writes exactly one user-controlled file."""
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "applied.txt"

        result = run_cli(
            ["proposals", "edit", "1", "--apply", "--output", str(out)],
            input_text="edited text\n",
        )

        assert out.exists()
        assert out.read_text().strip() == "edited text"
        assert "Applied to file" in result.stdout


def test_accept_apply_stdout_only():
    """Invariant: accept + apply without output writes only to stdout."""
    result = run_cli(
        ["proposals", "accept", "1", "--apply"],
    )

    assert "Applied Output" in result.stdout
    assert "example AI-generated phrasing suggestion" in result.stdout


def test_reject_has_no_side_effects():
    """Invariant: reject produces no files and no applied output."""
    result = run_cli(["proposals", "reject", "1"])

    assert "Applied" not in result.stdout


def test_approval_does_not_persist_across_runs():
    """
    Invariant: approving a proposal in one CLI invocation
    does not allow apply in a subsequent invocation.
    """

    # First run: accept proposal (no apply)
    result1 = run_cli(["proposals", "accept", "1"])
    assert "Proposal accepted" in result1.stdout

    # Second run: attempt to apply without approval in this session
    result2 = run_cli(["proposals", "edit", "1", "--output", "out.txt"])

    # No file should be created
    assert not Path("out.txt").exists()

    # No applied output should appear
    assert "Applied" not in result2.stdout

