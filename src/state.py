# src/state.py

from pathlib import Path

# Root-level state directory
STATE_DIR = Path(__file__).resolve().parent.parent / "state"

# Canonical SQL database path
DB_PATH = str(STATE_DIR / "letsappli_v1.sqlite3")