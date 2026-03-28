"""SQLite Developer repository implementation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from backlog_manager.domain.entities import Developer

if TYPE_CHECKING:
    import aiosqlite


class SQLiteDeveloperRepository:
    """SQLite implementation of DeveloperRepository."""

    def __init__(self, connection: aiosqlite.Connection) -> None:
        """Initialize repository.

        Args:
            connection: SQLite connection.
        """
        self._conn = connection

    async def add(self, developer: Developer) -> int:
        """Add a new developer.

        Args:
            developer: Developer to add.

        Returns:
            Generated ID for the developer.
        """
        cursor = await self._conn.execute(
            "INSERT INTO Developer (name) VALUES (?)",
            (developer.name,),
        )
        return cursor.lastrowid or 0

    async def get_by_id(self, developer_id: int) -> Developer | None:
        """Get developer by ID.

        Args:
            developer_id: Developer identifier.

        Returns:
            Developer if found, None otherwise.
        """
        async with self._conn.execute(
            "SELECT * FROM Developer WHERE id = ?", (developer_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            return self._row_to_developer(row)

    async def get_all(self) -> Sequence[Developer]:
        """Get all developers ordered by name.

        Returns:
            List of all developers.
        """
        async with self._conn.execute(
            "SELECT * FROM Developer ORDER BY name"
        ) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_developer(row) for row in rows]

    async def update(self, developer: Developer) -> None:
        """Update an existing developer.

        Args:
            developer: Developer with updated data.

        Raises:
            ValueError: If developer doesn't exist.
        """
        if developer.id is None or not await self.exists(developer.id):
            raise ValueError(f"Desenvolvedor {developer.id} nao existe")

        await self._conn.execute(
            "UPDATE Developer SET name = ? WHERE id = ?",
            (developer.name, developer.id),
        )

    async def delete(self, developer_id: int) -> None:
        """Delete a developer.

        Args:
            developer_id: ID of developer to delete.

        Raises:
            ValueError: If developer doesn't exist.
        """
        if not await self.exists(developer_id):
            raise ValueError(f"Desenvolvedor {developer_id} nao existe")

        await self._conn.execute("DELETE FROM Developer WHERE id = ?", (developer_id,))

    async def exists(self, developer_id: int) -> bool:
        """Check if developer exists.

        Args:
            developer_id: Developer ID.

        Returns:
            True if exists, False otherwise.
        """
        async with self._conn.execute(
            "SELECT 1 FROM Developer WHERE id = ?", (developer_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row is not None

    def _row_to_developer(self, row: aiosqlite.Row) -> Developer:
        """Convert database row to Developer entity.

        Args:
            row: Database row.

        Returns:
            Developer entity.
        """
        return Developer(
            id=row["id"],
            name=row["name"],
        )
