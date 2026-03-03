"""SQLite connection management."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import aiosqlite

if TYPE_CHECKING:
    pass

_SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_database_path() -> Path:
    """Get the database file path.

    Returns:
        Path to the SQLite database file.
    """
    app_data = Path(os.environ.get("APPDATA", Path.home()))
    db_dir = app_data / "BacklogManager" / "data"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "backlog.db"


async def create_connection(
    db_path: str | Path | None = None,
) -> aiosqlite.Connection:
    """Create async connection to SQLite database.

    Args:
        db_path: Path to database file. If None, uses default location.

    Returns:
        Async SQLite connection.
    """
    if db_path is None:
        db_path = get_database_path()

    conn = await aiosqlite.connect(db_path)
    await conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = aiosqlite.Row
    return conn


async def init_database(db_path: str | Path | None = None) -> None:
    """Initialize database with schema.

    Creates all tables if they don't exist.

    Args:
        db_path: Path to database file. If None, uses default location.
    """
    schema = _SCHEMA_PATH.read_text(encoding="utf-8")

    conn = await create_connection(db_path)
    try:
        await conn.executescript(schema)
        await conn.commit()
    finally:
        await conn.close()
