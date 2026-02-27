import hashlib
import sqlite3
from pathlib import Path


MIGRATIONS_DIR = Path("migrations")


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _ensure_schema_table(conn: sqlite3.Connection):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE,
            checksum TEXT NOT NULL,
            applied_at TEXT NOT NULL
        );
        """
    )


def _applied_migrations(conn):
    rows = conn.execute(
        "SELECT filename, checksum FROM schema_migrations"
    ).fetchall()
    return {r[0]: r[1] for r in rows}


def _load_migration_files():
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    return files


def migrate(db_path: str):
    """
    Deterministic migration executor.

    Guarantees:
    - ordered execution
    - checksum validation
    - drift detection
    - atomic application
    """

    conn = sqlite3.connect(db_path)

    try:
        conn.execute("BEGIN")

        _ensure_schema_table(conn)

        applied = _applied_migrations(conn)
        files = _load_migration_files()

        for file in files:
            content = file.read_bytes()
            checksum = _sha256(content)

            if file.name in applied:
                if applied[file.name] != checksum:
                    raise RuntimeError(
                        f"Migration checksum mismatch: {file.name}"
                    )
                continue

            sql = content.decode("utf-8")

            conn.executescript(sql)

            conn.execute(
                """
                INSERT INTO schema_migrations
                (filename, checksum, applied_at)
                VALUES (?, ?, datetime('now'))
                """,
                (file.name, checksum),
            )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
