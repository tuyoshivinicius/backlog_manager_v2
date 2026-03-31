"""SQLite Story repository implementation."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from typing import TYPE_CHECKING

from backlog_manager.domain.entities import Story
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus

if TYPE_CHECKING:
    import aiosqlite


class SQLiteStoryRepository:
    """SQLite implementation of StoryRepository."""

    def __init__(self, connection: aiosqlite.Connection) -> None:
        """Initialize repository.

        Args:
            connection: SQLite connection.
        """
        self._conn = connection

    async def add(self, story: Story) -> None:
        """Add a new story.

        Args:
            story: Story to add.

        Raises:
            ValueError: If story with same ID already exists.
        """
        if await self.exists(story.id):
            raise ValueError(f"Historia com ID {story.id} ja existe")

        await self._conn.execute(
            """
            INSERT INTO Story (
                id, component, name, story_points, priority, status,
                duration, start_date, end_date, developer_id, feature_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                story.id,
                story.component,
                story.name,
                int(story.story_points),
                story.priority,
                str(story.status),
                story.duration,
                story.start_date.isoformat() if story.start_date else None,
                story.end_date.isoformat() if story.end_date else None,
                story.developer_id,
                story.feature_id,
            ),
        )

    async def get_by_id(self, story_id: str) -> Story | None:
        """Get story by ID.

        Args:
            story_id: Story identifier.

        Returns:
            Story if found, None otherwise.
        """
        async with self._conn.execute(
            "SELECT * FROM Story WHERE id = ?", (story_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            return self._row_to_story(row)

    async def get_all(self) -> Sequence[Story]:
        """Get all stories ordered by priority.

        Returns:
            List of all stories.
        """
        async with self._conn.execute(
            "SELECT * FROM Story ORDER BY priority"
        ) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_story(row) for row in rows]

    async def get_by_status(self, status: str) -> Sequence[Story]:
        """Get stories by status.

        Args:
            status: Status to filter by.

        Returns:
            List of stories with the specified status.
        """
        async with self._conn.execute(
            "SELECT * FROM Story WHERE status = ? ORDER BY priority", (status,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_story(row) for row in rows]

    async def get_by_developer(self, developer_id: int) -> Sequence[Story]:
        """Get stories assigned to a developer.

        Args:
            developer_id: Developer ID.

        Returns:
            List of stories assigned to the developer.
        """
        async with self._conn.execute(
            "SELECT * FROM Story WHERE developer_id = ? ORDER BY priority",
            (developer_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_story(row) for row in rows]

    async def get_by_feature(self, feature_id: int) -> Sequence[Story]:
        """Get stories in a feature.

        Args:
            feature_id: Feature ID.

        Returns:
            List of stories in the feature.
        """
        async with self._conn.execute(
            "SELECT * FROM Story WHERE feature_id = ? ORDER BY priority",
            (feature_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_story(row) for row in rows]

    async def update(self, story: Story) -> None:
        """Update an existing story.

        Args:
            story: Story with updated data.

        Raises:
            ValueError: If story doesn't exist.
        """
        if not await self.exists(story.id):
            raise ValueError(f"Historia {story.id} nao existe")

        await self._conn.execute(
            """
            UPDATE Story SET
                component = ?, name = ?, story_points = ?, priority = ?,
                status = ?, duration = ?, start_date = ?, end_date = ?,
                developer_id = ?, feature_id = ?
            WHERE id = ?
            """,
            (
                story.component,
                story.name,
                int(story.story_points),
                story.priority,
                str(story.status),
                story.duration,
                story.start_date.isoformat() if story.start_date else None,
                story.end_date.isoformat() if story.end_date else None,
                story.developer_id,
                story.feature_id,
                story.id,
            ),
        )

    async def delete(self, story_id: str) -> None:
        """Delete a story.

        Args:
            story_id: ID of story to delete.

        Raises:
            ValueError: If story doesn't exist.
        """
        if not await self.exists(story_id):
            raise ValueError(f"Historia {story_id} nao existe")

        await self._conn.execute("DELETE FROM Story WHERE id = ?", (story_id,))

    async def exists(self, story_id: str) -> bool:
        """Check if story exists.

        Args:
            story_id: Story ID.

        Returns:
            True if exists, False otherwise.
        """
        async with self._conn.execute(
            "SELECT 1 FROM Story WHERE id = ?", (story_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row is not None

    async def get_max_id_number(self, component: str) -> int:
        """Get max sequential number for a component.

        Args:
            component: Component name (case-insensitive).

        Returns:
            Max number found or 0 if none.
        """
        async with self._conn.execute(
            """
            SELECT COALESCE(
                MAX(CAST(SUBSTR(id, INSTR(id, '-') + 1) AS INTEGER)),
                0
            )
            FROM Story
            WHERE UPPER(component) = UPPER(?)
            """,
            (component,),
        ) as cursor:
            row = await cursor.fetchone()
            return int(row[0]) if row else 0

    async def get_max_priority(self) -> int:
        """Get max priority in backlog.

        Returns:
            Max priority or -1 if empty.
        """
        async with self._conn.execute(
            "SELECT COALESCE(MAX(priority), -1) FROM Story"
        ) as cursor:
            row = await cursor.fetchone()
            return int(row[0]) if row else -1

    async def get_by_priority(self, priority: int) -> Story | None:
        """Get story by exact priority.

        Args:
            priority: Priority to search.

        Returns:
            Story if found, None otherwise.
        """
        async with self._conn.execute(
            "SELECT * FROM Story WHERE priority = ?", (priority,)
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            return self._row_to_story(row)

    async def count_by_developer(self, developer_id: int) -> int:
        """Count stories assigned to a developer.

        Args:
            developer_id: Developer ID.

        Returns:
            Number of stories assigned (0 if none).
        """
        async with self._conn.execute(
            "SELECT COUNT(*) FROM Story WHERE developer_id = ?",
            (developer_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return int(row[0]) if row else 0

    def _row_to_story(self, row: aiosqlite.Row) -> Story:
        """Convert database row to Story entity.

        Args:
            row: Database row.

        Returns:
            Story entity.
        """
        start_date = None
        if row["start_date"]:
            start_date = date.fromisoformat(row["start_date"])

        end_date = None
        if row["end_date"]:
            end_date = date.fromisoformat(row["end_date"])

        return Story(
            id=row["id"],
            component=row["component"],
            name=row["name"],
            story_points=StoryPoint(row["story_points"]),
            priority=row["priority"],
            status=StoryStatus(row["status"]),
            duration=row["duration"],
            start_date=start_date,
            end_date=end_date,
            developer_id=row["developer_id"],
            feature_id=row["feature_id"],
        )
