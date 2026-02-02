import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from phase5.cli import main as phase5_main  # noqa: E402


if __name__ == "__main__":
    phase5_main()

