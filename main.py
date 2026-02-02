import os
import sys

# Ensure "src" is import root so `import discovery`, `import phase5`, etc. work.
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from discovery.cli import main as discovery_main  # noqa: E402


if __name__ == "__main__":
    discovery_main()

