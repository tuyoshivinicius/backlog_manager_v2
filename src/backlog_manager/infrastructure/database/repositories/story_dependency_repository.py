"""SQLite Story Dependency repository implementation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import aiosqlite


class SQLiteStoryDependencyRepository:
    """SQLite implementation of StoryDependencyRepository."""

    def __init__(self, connection: aiosqlite.Connection) -> None:
        """Initialize repository.

        Args:
            connection: SQLite connection.
        """
        self._conn = connection

    async def add(self, planning_id: int, story_id: str, depends_on_id: str) -> None:
        """Add a dependency between stories.

        Args:
            planning_id: Planning ID for scoping.
            story_id: ID of the story that depends.
            depends_on_id: ID of the story it depends on.

        Raises:
            ValueError: If dependency already exists or stories don't exist.
        """
        if story_id == depends_on_id:
            raise ValueError("Historia nao pode depender de si mesma")

        if await self.exists(planning_id, story_id, depends_on_id):
            raise ValueError(f"Dependencia {story_id} -> {depends_on_id} ja existe")

        await self._conn.execute(
            "INSERT INTO Story_Dependency (planning_id, story_id, depends_on_id) "
            "VALUES (?, ?, ?)",
            (planning_id, story_id, depends_on_id),
        )

    async def remove(self, planning_id: int, story_id: str, depends_on_id: str) -> None:
        """Remove a dependency between stories.

        Args:
            planning_id: Planning ID for scoping.
            story_id: ID of the story that depends.
            depends_on_id: ID of the story it depends on.

        Raises:
            ValueError: If dependency doesn't exist.
        """
        if not await self.exists(planning_id, story_id, depends_on_id):
            raise ValueError(f"Dependencia {story_id} -> {depends_on_id} nao existe")

        await self._conn.execute(
            "DELETE FROM Story_Dependency "
            "WHERE planning_id = ? AND story_id = ? AND depends_on_id = ?",
            (planning_id, story_id, depends_on_id),
        )

    async def get_dependencies(self, planning_id: int, story_id: str) -> Sequence[str]:
        """Get IDs of stories that a story depends on.

        Args:
            planning_id: Planning ID for scoping.
            story_id: Story ID.

        Returns:
            List of dependency IDs.
        """
        async with self._conn.execute(
            "SELECT depends_on_id FROM Story_Dependency "
            "WHERE planning_id = ? AND story_id = ?",
            (planning_id, story_id),
        ) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def get_dependents(self, planning_id: int, story_id: str) -> Sequence[str]:
        """Get IDs of stories that depend on a story.

        Args:
            planning_id: Planning ID for scoping.
            story_id: Story ID.

        Returns:
            List of dependent story IDs.
        """
        async with self._conn.execute(
            "SELECT story_id FROM Story_Dependency "
            "WHERE planning_id = ? AND depends_on_id = ?",
            (planning_id, story_id),
        ) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def exists(self, planning_id: int, story_id: str, depends_on_id: str) -> bool:
        """Check if dependency exists.

        Args:
            planning_id: Planning ID for scoping.
            story_id: ID of the story that depends.
            depends_on_id: ID of the story it depends on.

        Returns:
            True if exists, False otherwise.
        """
        async with self._conn.execute(
            """
            SELECT 1 FROM Story_Dependency
            WHERE planning_id = ? AND story_id = ? AND depends_on_id = ?
            """,
            (planning_id, story_id, depends_on_id),
        ) as cursor:
            row = await cursor.fetchone()
            return row is not None

    async def get_all_dependencies(self, planning_id: int) -> Sequence[tuple[str, str]]:
        """Get all dependencies for a planning.

        Args:
            planning_id: Planning ID for scoping.

        Returns:
            List of (story_id, depends_on_id) tuples.
        """
        async with self._conn.execute(
            "SELECT story_id, depends_on_id FROM Story_Dependency "
            "WHERE planning_id = ?",
            (planning_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [(row[0], row[1]) for row in rows]

    async def remove_all_for_story(self, planning_id: int, story_id: str) -> None:
        """Remove all dependencies where the story appears.

        Args:
            planning_id: Planning ID for scoping.
            story_id: ID of the story.

        Note:
            Removes where story_id is the dependent AND where it is the dependency.
        """
        await self._conn.execute(
            "DELETE FROM Story_Dependency "
            "WHERE planning_id = ? AND (story_id = ? OR depends_on_id = ?)",
            (planning_id, story_id, story_id),
        )
