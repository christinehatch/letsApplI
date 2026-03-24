# src/state.py

import os
from pathlib import Path

# Default root-level state directory (local development).
_LOCAL_STATE_DIR = Path(__file__).resolve().parent.parent / "state"

# Render instances are ephemeral; use /tmp unless explicitly overridden.
_DEFAULT_DB_PATH = (
    Path("/tmp/letsappli/letsappli_v1.sqlite3")
    if os.getenv("RENDER")
    else _LOCAL_STATE_DIR / "letsappli_v1.sqlite3"
)

# Canonical SQL database path (env override supported).
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
DB_PATH = DATABASE_URL or os.getenv("DB_PATH", str(_DEFAULT_DB_PATH))

# File-based state directory is only meaningful for local/SQLite usage.
if DB_PATH.startswith("postgres://") or DB_PATH.startswith("postgresql://"):
    STATE_DIR = Path(os.getenv("STATE_DIR", "/tmp/letsappli"))
else:
    STATE_DIR = Path(DB_PATH).parent
