import os
import subprocess
import sys


def run_cli(args):
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    result = subprocess.run(
        [sys.executable, "-m", "phase5.cli"] + args,
        capture_output=True,
        text=True,
        env=env,
    )
    return result.stdout, result.stderr


def test_shadow_mode_does_not_change_cli_output():
    """
    Invariant:
    Enabling Phase 5.7 shadow-mode LLM execution
    must not change any CLI-visible output.
    """

    # Baseline run (LLM disabled)
    os.environ.pop("USE_LLM_SHADOW_MODE", None)
    baseline_out, _ = run_cli(["proposals"])

    # Shadow mode run (LLM enabled)
    os.environ["USE_LLM_SHADOW_MODE"] = "1"
    shadow_out, _ = run_cli(["proposals"])

    assert baseline_out == shadow_out

