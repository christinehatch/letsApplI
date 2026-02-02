import subprocess
import sys
from pathlib import Path
import os


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

    env = os.environ.copy()
    env["PYTHONPATH"] = "src" + (
        os.pathsep + env["PYTHONPATH"] if "PYTHONPATH" in env else ""
    )

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
    )

    return result.stdout, result.stderr

