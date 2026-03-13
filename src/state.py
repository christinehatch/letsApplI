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
DB_PATH = os.getenv("DB_PATH", str(_DEFAULT_DB_PATH))
STATE_DIR = Path(DB_PATH).parent
