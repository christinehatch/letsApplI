import subprocess
import sys
from pathlib import Path


def run_cli(args):
    """
    Run the phase5 CLI as a subprocess and capture stdout/stderr.

    Returns:
        (stdout: str, stderr: str)
    """
    cmd = [
        sys.executable,
        "-m",
        "phase5.cli",
        *args,
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=None,  # inherit environment (important for USE_LLM_SHADOW_MODE)
    )

    return result.stdout, result.stderr

