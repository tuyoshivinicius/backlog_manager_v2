"""SQLite Unit of Work implementation."""

from __future__ import annotations

from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING

from backlog_manager.infrastructure.database.repositories import (
    SQLiteDeveloperRepository,
    SQLiteFeatureRepository,
    SQLiteStoryDependencyRepository,
    SQLiteStoryRepository,
)
from backlog_manager.infrastructure.database.sqlite_connection import create_connection

if TYPE_CHECKING:
    import aiosqlite


class SQLiteUnitOfWork:
    """SQLite implementation of Unit of Work pattern.

    Manages database transactions and provides access to repositories.

    Example:
        async with SQLiteUnitOfWork() as uow:
            dev_id = await uow.developers.add(Developer(name="John"))
            await uow.commit()
    """

    def __init__(self, db_path: str | Path | None = None) -> None:
        """Initialize Unit of Work.

        Args:
            db_path: Path to database file. If None, uses default location.
        """
        self._db_path = db_path
        self._conn: aiosqlite.Connection | None = None
        self._stories: SQLiteStoryRepository | None = None
        self._developers: SQLiteDeveloperRepository | None = None
        self._features: SQLiteFeatureRepository | None = None
        self._dependencies: SQLiteStoryDependencyRepository | None = None

    @property
    def stories(self) -> SQLiteStoryRepository:
        """Get story repository.

        Returns:
            Story repository instance.

        Raises:
            RuntimeError: If not in context.
        """
        if self._stories is None:
            raise RuntimeError("UnitOfWork must be used as context manager")
        return self._stories

    @property
    def developers(self) -> SQLiteDeveloperRepository:
        """Get developer repository.

        Returns:
            Developer repository instance.

        Raises:
            RuntimeError: If not in context.
        """
        if self._developers is None:
            raise RuntimeError("UnitOfWork must be used as context manager")
        return self._developers

    @property
    def features(self) -> SQLiteFeatureRepository:
        """Get feature repository.

        Returns:
            Feature repository instance.

        Raises:
            RuntimeError: If not in context.
        """
        if self._features is None:
            raise RuntimeError("UnitOfWork must be used as context manager")
        return self._features

    @property
    def dependencies(self) -> SQLiteStoryDependencyRepository:
        """Get story dependency repository.

        Returns:
            Story dependency repository instance.

        Raises:
            RuntimeError: If not in context.
        """
        if self._dependencies is None:
            raise RuntimeError("UnitOfWork must be used as context manager")
        return self._dependencies

    async def __aenter__(self) -> SQLiteUnitOfWork:
        """Enter async context and start transaction.

        Returns:
            Self for use in async with statement.
        """
        self._conn = await create_connection(self._db_path)
        self._stories = SQLiteStoryRepository(self._conn)
        self._developers = SQLiteDeveloperRepository(self._conn)
        self._features = SQLiteFeatureRepository(self._conn)
        self._dependencies = SQLiteStoryDependencyRepository(self._conn)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit async context with commit or rollback.

        Args:
            exc_type: Exception type if error occurred.
            exc_val: Exception value if error occurred.
            exc_tb: Exception traceback if error occurred.
        """
        if self._conn is None:
            return

        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()

        await self._conn.close()
        self._conn = None
        self._stories = None
        self._developers = None
        self._features = None
        self._dependencies = None

    async def commit(self) -> None:
        """Commit the current transaction."""
        if self._conn is not None:
            await self._conn.commit()

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        if self._conn is not None:
            await self._conn.rollback()
