"""SQLite connection management."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

import aiosqlite

if TYPE_CHECKING:
    pass  # Required for conditional imports used by type checkers only

_SCHEMA_PATH = Path(__file__).parent / "schema.sql"

logger = logging.getLogger(__name__)


def get_database_path() -> Path:
    """Get the database file path.

    Priority:
    1. BACKLOG_DB_PATH environment variable (if set)
    2. Default app data location: %APPDATA%/BacklogManager/data/backlog.db

    Returns:
        Path to the SQLite database file.
    """
    env_path = os.environ.get("BACKLOG_DB_PATH")
    if env_path:
        return Path(env_path)

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


async def _needs_planning_migration(conn: aiosqlite.Connection) -> bool:
    """Check if database needs planning migration.

    Detects old schema by checking if Story table has planning_id column.

    Args:
        conn: Active database connection.

    Returns:
        True if migration is needed, False otherwise.
    """
    cursor = await conn.execute("PRAGMA table_info(Story)")
    columns = await cursor.fetchall()
    if not columns:
        # Story table doesn't exist yet — fresh install, no migration needed
        return False
    column_names = [col[1] for col in columns]
    return "planning_id" not in column_names


async def _migrate_to_planning_schema(conn: aiosqlite.Connection) -> None:
    """Migrate database from old schema (Story without planning_id) to new schema.

    Steps:
    1. Create Planning table
    2. Insert default "Planejamento Inicial"
    3. Rename old tables
    4. Create new tables with composite PKs
    5. Copy data with default planning_id
    6. Drop old tables
    7. Recreate indices

    Args:
        conn: Active database connection.
    """
    logger.info("Starting planning schema migration...")

    # 1. Create Planning table
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS Planning (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(200) NOT NULL UNIQUE,
            created_at TIMESTAMP NOT NULL DEFAULT (datetime('now')),
            updated_at TIMESTAMP NOT NULL DEFAULT (datetime('now'))
        )
    """
    )

    # 2. Insert default planning
    await conn.execute(
        "INSERT INTO Planning (name) VALUES (?)", ("Planejamento Inicial",)
    )

    # 3. Get the default planning ID
    cursor = await conn.execute(
        "SELECT id FROM Planning WHERE name = ?", ("Planejamento Inicial",)
    )
    row = await cursor.fetchone()
    assert row is not None, "Default planning row must exist"
    default_planning_id = row[0]

    # 4. Rename old tables
    await conn.execute("ALTER TABLE Story_Dependency RENAME TO Story_Dependency_old")
    await conn.execute("ALTER TABLE Story RENAME TO Story_old")

    # 5. Create new Story table with composite PK
    await conn.execute(
        """
        CREATE TABLE Story (
            planning_id INTEGER NOT NULL REFERENCES Planning(id) ON DELETE CASCADE,
            id VARCHAR(20) NOT NULL,
            component VARCHAR(50) NOT NULL,
            name VARCHAR(200) NOT NULL,
            story_points INTEGER NOT NULL CHECK (story_points IN (3, 5, 8, 13)),
            priority INTEGER NOT NULL CHECK (priority >= 0),
            status VARCHAR(20) NOT NULL DEFAULT 'BACKLOG',
            duration INTEGER,
            start_date DATE,
            end_date DATE,
            developer_id INTEGER REFERENCES Developer(id) ON DELETE SET NULL,
            feature_id INTEGER REFERENCES Feature(id) ON DELETE SET NULL,
            PRIMARY KEY (planning_id, id)
        )
    """
    )

    # 6. Copy data with default planning_id
    await conn.execute(
        """
        INSERT INTO Story (planning_id, id, component, name, story_points, priority,
                          status, duration, start_date, end_date, developer_id, feature_id)
        SELECT ?, id, component, name, story_points, priority,
               status, duration, start_date, end_date, developer_id, feature_id
        FROM Story_old
        """,
        (default_planning_id,),
    )

    # 7. Create new Story_Dependency table with composite FK
    await conn.execute(
        """
        CREATE TABLE Story_Dependency (
            planning_id INTEGER NOT NULL,
            story_id VARCHAR(20) NOT NULL,
            depends_on_id VARCHAR(20) NOT NULL,
            PRIMARY KEY (planning_id, story_id, depends_on_id),
            FOREIGN KEY (planning_id, story_id)
                REFERENCES Story(planning_id, id) ON DELETE CASCADE,
            FOREIGN KEY (planning_id, depends_on_id)
                REFERENCES Story(planning_id, id) ON DELETE CASCADE,
            CHECK (story_id != depends_on_id)
        )
    """
    )

    # 8. Copy dependency data
    await conn.execute(
        """
        INSERT INTO Story_Dependency (planning_id, story_id, depends_on_id)
        SELECT ?, story_id, depends_on_id
        FROM Story_Dependency_old
        """,
        (default_planning_id,),
    )

    # 9. Drop old tables
    await conn.execute("DROP TABLE Story_Dependency_old")
    await conn.execute("DROP TABLE Story_old")

    # 10. Create indices
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_planning_name ON Planning(name)")
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_story_planning ON Story(planning_id)"
    )
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_story_status ON Story(planning_id, status)"
    )
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_story_developer "
        "ON Story(planning_id, developer_id)"
    )
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_story_feature "
        "ON Story(planning_id, feature_id)"
    )
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_story_priority "
        "ON Story(planning_id, priority)"
    )

    await conn.commit()
    logger.info(
        "Planning schema migration completed. "
        "Stories migrated to 'Planejamento Inicial' (id=%d)",
        default_planning_id,
    )


async def init_database(db_path: str | Path | None = None) -> None:
    """Initialize database with schema.

    Creates all tables if they don't exist. If old schema is detected
    (Story without planning_id), runs automatic migration.

    Args:
        db_path: Path to database file. If None, uses default location.
    """
    conn = await create_connection(db_path)
    try:
        # Check if migration is needed before applying new schema
        if await _needs_planning_migration(conn):
            await _migrate_to_planning_schema(conn)
        else:
            # Apply schema (CREATE IF NOT EXISTS is safe for existing tables)
            schema = _SCHEMA_PATH.read_text(encoding="utf-8")
            await conn.executescript(schema)
            await conn.commit()
    finally:
        await conn.close()
