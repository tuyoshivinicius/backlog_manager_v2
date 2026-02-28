"""SQLite Feature repository implementation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from backlog_manager.domain.entities import Feature
from backlog_manager.domain.exceptions import (
    DuplicateWaveException,
    FeatureHasStoriesException,
)

if TYPE_CHECKING:
    import aiosqlite


class SQLiteFeatureRepository:
    """SQLite implementation of FeatureRepository."""

    def __init__(self, connection: aiosqlite.Connection) -> None:
        """Initialize repository.

        Args:
            connection: SQLite connection.
        """
        self._conn = connection

    async def add(self, feature: Feature) -> int:
        """Add a new feature.

        Args:
            feature: Feature to add.

        Returns:
            Generated ID for the feature.

        Raises:
            DuplicateWaveException: If wave already exists.
            ValueError: If name already exists.
        """
        existing = await self.get_by_wave(feature.wave)
        if existing:
            raise DuplicateWaveException(
                wave=feature.wave,
                existing_feature_name=existing.name,
            )

        try:
            cursor = await self._conn.execute(
                "INSERT INTO Feature (name, wave) VALUES (?, ?)",
                (feature.name, feature.wave),
            )
            return cursor.lastrowid or 0
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError(f"Feature com nome '{feature.name}' ja existe") from e
            raise

    async def get_by_id(self, feature_id: int) -> Feature | None:
        """Get feature by ID.

        Args:
            feature_id: Feature identifier.

        Returns:
            Feature if found, None otherwise.
        """
        async with self._conn.execute(
            "SELECT * FROM Feature WHERE id = ?", (feature_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            return self._row_to_feature(row)

    async def get_by_wave(self, wave: int) -> Feature | None:
        """Get feature by wave number.

        Args:
            wave: Wave number.

        Returns:
            Feature if found, None otherwise.
        """
        async with self._conn.execute(
            "SELECT * FROM Feature WHERE wave = ?", (wave,)
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            return self._row_to_feature(row)

    async def get_all(self) -> Sequence[Feature]:
        """Get all features ordered by wave.

        Returns:
            List of all features.
        """
        async with self._conn.execute(
            "SELECT * FROM Feature ORDER BY wave"
        ) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_feature(row) for row in rows]

    async def update(self, feature: Feature) -> None:
        """Update an existing feature.

        Args:
            feature: Feature with updated data.

        Raises:
            ValueError: If feature doesn't exist.
            DuplicateWaveException: If new wave already exists.
        """
        if feature.id is None or not await self.exists(feature.id):
            raise ValueError(f"Feature {feature.id} nao existe")

        existing = await self.get_by_wave(feature.wave)
        if existing and existing.id != feature.id:
            raise DuplicateWaveException(
                wave=feature.wave,
                existing_feature_name=existing.name,
            )

        await self._conn.execute(
            "UPDATE Feature SET name = ?, wave = ? WHERE id = ?",
            (feature.name, feature.wave, feature.id),
        )

    async def delete(self, feature_id: int) -> None:
        """Delete a feature.

        Args:
            feature_id: ID of feature to delete.

        Raises:
            ValueError: If feature doesn't exist.
            FeatureHasStoriesException: If feature has stories.
        """
        feature = await self.get_by_id(feature_id)
        if feature is None:
            raise ValueError(f"Feature {feature_id} nao existe")

        story_count = await self._count_stories(feature_id)
        if story_count > 0:
            raise FeatureHasStoriesException(
                feature_id=feature_id,
                feature_name=feature.name,
                story_count=story_count,
            )

        await self._conn.execute(
            "DELETE FROM Feature WHERE id = ?", (feature_id,)
        )

    async def exists(self, feature_id: int) -> bool:
        """Check if feature exists.

        Args:
            feature_id: Feature ID.

        Returns:
            True if exists, False otherwise.
        """
        async with self._conn.execute(
            "SELECT 1 FROM Feature WHERE id = ?", (feature_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row is not None

    async def has_stories(self, feature_id: int) -> bool:
        """Check if feature has stories.

        Args:
            feature_id: Feature ID.

        Returns:
            True if has stories, False otherwise.
        """
        return await self._count_stories(feature_id) > 0

    async def _count_stories(self, feature_id: int) -> int:
        """Count stories in a feature.

        Args:
            feature_id: Feature ID.

        Returns:
            Number of stories.
        """
        async with self._conn.execute(
            "SELECT COUNT(*) FROM Story WHERE feature_id = ?", (feature_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

    def _row_to_feature(self, row: aiosqlite.Row) -> Feature:
        """Convert database row to Feature entity.

        Args:
            row: Database row.

        Returns:
            Feature entity.
        """
        return Feature(
            id=row["id"],
            name=row["name"],
            wave=row["wave"],
        )
