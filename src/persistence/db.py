from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from contextlib import contextmanager
from typing import Any


def _is_postgres_url(value: str) -> bool:
    lowered = value.strip().lower()
    return lowered.startswith("postgres://") or lowered.startswith("postgresql://")


class DBRow(Mapping[str, Any]):
    def __init__(self, columns: list[str], values: tuple[Any, ...]):
        self._columns = columns
        self._values = values
        self._index = {name: idx for idx, name in enumerate(columns)}

    def __getitem__(self, key: str | int) -> Any:
        if isinstance(key, int):
            return self._values[key]
        return self._values[self._index[key]]

    def __iter__(self):
        return iter(self._columns)

    def __len__(self) -> int:
        return len(self._columns)


class PostgresResult:
    def __init__(self, cursor):
        self._cursor = cursor
        self._columns = [desc.name for desc in cursor.description] if cursor.description else []

    def fetchone(self):
        raw = self._cursor.fetchone()
        if raw is None:
            return None
        return DBRow(self._columns, raw)

    def fetchall(self):
        rows = self._cursor.fetchall()
        return [DBRow(self._columns, row) for row in rows]


class PostgresConnection:
    backend = "postgres"

    def __init__(self, dsn: str):
        from psycopg import connect

        self._conn = connect(dsn)

    @staticmethod
    def _adapt_sql(sql: str) -> str:
        # SQLite placeholder style -> PostgreSQL style.
        return sql.replace("?", "%s").replace("datetime('now')", "CURRENT_TIMESTAMP")

    def execute(self, sql: str, params: tuple[Any, ...] | list[Any] = ()):
        cursor = self._conn.cursor()
        cursor.execute(self._adapt_sql(sql), tuple(params))
        return PostgresResult(cursor)

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        self._conn.close()


class SQLiteConnection:
    backend = "sqlite"

    def __init__(self, db_path: str):
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON;")

    def execute(self, sql: str, params: tuple[Any, ...] | list[Any] = ()):
        return self._conn.execute(sql, tuple(params))

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        self._conn.close()


def get_connection(db_path: str):
    if _is_postgres_url(db_path):
        return PostgresConnection(db_path)
    return SQLiteConnection(db_path)


@contextmanager
def transactional(conn):
    try:
        conn.execute("BEGIN")
        yield
        conn.commit()
    except Exception:
        conn.rollback()
        raise
