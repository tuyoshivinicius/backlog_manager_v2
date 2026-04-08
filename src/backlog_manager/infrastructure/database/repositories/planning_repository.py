"""SQLite Planning repository implementation."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import TYPE_CHECKING

from backlog_manager.domain.entities import Planning

if TYPE_CHECKING:
    import aiosqlite


class SQLitePlanningRepository:
    """SQLite implementation of PlanningRepository."""

    def __init__(self, connection: aiosqlite.Connection) -> None:
        """Initialize repository.

        Args:
            connection: SQLite connection.
        """
        self._conn = connection

    async def add(self, planning: Planning) -> int:
        """Add a new planning.

        Args:
            planning: Planning to add.

        Returns:
            Generated ID for the planning.
        """
        cursor = await self._conn.execute(
            "INSERT INTO Planning (name) VALUES (?)",
            (planning.name,),
        )
        return cursor.lastrowid  # type: ignore[return-value]

    async def get_by_id(self, planning_id: int) -> Planning | None:
        """Get planning by ID.

        Args:
            planning_id: Planning identifier.

        Returns:
            Planning if found, None otherwise.
        """
        async with self._conn.execute(
            "SELECT * FROM Planning WHERE id = ?", (planning_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            return self._row_to_planning(row)

    async def get_by_name(self, name: str) -> Planning | None:
        """Get planning by exact name.

        Args:
            name: Planning name.

        Returns:
            Planning if found, None otherwise.
        """
        async with self._conn.execute(
            "SELECT * FROM Planning WHERE name = ?", (name,)
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            return self._row_to_planning(row)

    async def get_all(self) -> Sequence[Planning]:
        """Get all plannings ordered by name.

        Returns:
            List of all plannings.
        """
        async with self._conn.execute("SELECT * FROM Planning ORDER BY name") as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_planning(row) for row in rows]

    async def update(self, planning: Planning) -> None:
        """Update an existing planning.

        Args:
            planning: Planning with updated data.

        Raises:
            ValueError: If planning doesn't exist.
        """
        if planning.id is None or not await self.exists(planning.id):
            raise ValueError(f"Planejamento {planning.id} nao existe")

        await self._conn.execute(
            """
            UPDATE Planning SET name = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (planning.name, planning.id),
        )

    async def delete(self, planning_id: int) -> None:
        """Delete a planning (cascade deletes stories).

        Args:
            planning_id: ID of planning to delete.

        Raises:
            ValueError: If planning doesn't exist.
        """
        if not await self.exists(planning_id):
            raise ValueError(f"Planejamento {planning_id} nao existe")

        await self._conn.execute("DELETE FROM Planning WHERE id = ?", (planning_id,))

    async def exists(self, planning_id: int) -> bool:
        """Check if planning exists.

        Args:
            planning_id: Planning ID.

        Returns:
            True if exists, False otherwise.
        """
        async with self._conn.execute(
            "SELECT 1 FROM Planning WHERE id = ?", (planning_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row is not None

    async def count_stories(self, planning_id: int) -> int:
        """Count stories in a planning.

        Args:
            planning_id: Planning ID.

        Returns:
            Number of stories.
        """
        async with self._conn.execute(
            "SELECT COUNT(*) FROM Story WHERE planning_id = ?",
            (planning_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return int(row[0]) if row else 0

    async def update_timestamp(self, planning_id: int) -> None:
        """Update the updated_at timestamp to now.

        Args:
            planning_id: Planning ID.
        """
        await self._conn.execute(
            "UPDATE Planning SET updated_at = datetime('now') WHERE id = ?",
            (planning_id,),
        )

    def _row_to_planning(self, row: aiosqlite.Row) -> Planning:
        """Convert database row to Planning entity.

        Args:
            row: Database row.

        Returns:
            Planning entity.
        """
        created_at = None
        if row["created_at"]:
            created_at = datetime.fromisoformat(row["created_at"])

        updated_at = None
        if row["updated_at"]:
            updated_at = datetime.fromisoformat(row["updated_at"])

        return Planning(
            id=row["id"],
            name=row["name"],
            created_at=created_at,
            updated_at=updated_at,
        )
