"""Test SQLite Story Dependency Repository."""

import tempfile
from pathlib import Path

import pytest

from backlog_manager.domain.entities import Story
from backlog_manager.domain.value_objects import StoryPoint
from backlog_manager.infrastructure.database import SQLiteUnitOfWork, init_database


@pytest.mark.integration
@pytest.mark.asyncio
class TestStoryDependencyRepository:
    """Test Story Dependency repository operations."""

    @pytest.fixture
    def db_path(self):
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir) / "test.db"

    async def _create_stories(self, uow: SQLiteUnitOfWork) -> None:
        """Helper to create test stories."""
        for i in range(1, 4):
            await uow.stories.add(
                Story(
                    id=f"TEST-{i:03d}",
                    component="TEST",
                    name=f"Story {i}",
                    story_points=StoryPoint.SMALL,
                    priority=i,
                )
            )

    async def test_add_dependency(self, db_path: Path) -> None:
        """Test adding a dependency."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_stories(uow)
            await uow.dependencies.add("TEST-002", "TEST-001")

        async with SQLiteUnitOfWork(db_path) as uow:
            deps = await uow.dependencies.get_dependencies("TEST-002")
            assert "TEST-001" in deps

    async def test_add_duplicate_raises_error(self, db_path: Path) -> None:
        """Test adding duplicate dependency raises ValueError."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_stories(uow)
            await uow.dependencies.add("TEST-002", "TEST-001")

        with pytest.raises(ValueError, match="ja existe"):
            async with SQLiteUnitOfWork(db_path) as uow:
                await uow.dependencies.add("TEST-002", "TEST-001")

    async def test_remove_dependency(self, db_path: Path) -> None:
        """Test removing a dependency."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_stories(uow)
            await uow.dependencies.add("TEST-002", "TEST-001")

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.dependencies.remove("TEST-002", "TEST-001")

        async with SQLiteUnitOfWork(db_path) as uow:
            deps = await uow.dependencies.get_dependencies("TEST-002")
            assert "TEST-001" not in deps

    async def test_remove_nonexistent_raises_error(self, db_path: Path) -> None:
        """Test removing nonexistent dependency raises ValueError."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_stories(uow)

        with pytest.raises(ValueError, match="nao existe"):
            async with SQLiteUnitOfWork(db_path) as uow:
                await uow.dependencies.remove("TEST-002", "TEST-001")

    async def test_get_dependencies(self, db_path: Path) -> None:
        """Test getting dependencies of a story."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_stories(uow)
            await uow.dependencies.add("TEST-003", "TEST-001")
            await uow.dependencies.add("TEST-003", "TEST-002")

        async with SQLiteUnitOfWork(db_path) as uow:
            deps = await uow.dependencies.get_dependencies("TEST-003")
            assert len(deps) == 2
            assert "TEST-001" in deps
            assert "TEST-002" in deps

    async def test_get_dependents(self, db_path: Path) -> None:
        """Test getting stories that depend on a story."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_stories(uow)
            await uow.dependencies.add("TEST-002", "TEST-001")
            await uow.dependencies.add("TEST-003", "TEST-001")

        async with SQLiteUnitOfWork(db_path) as uow:
            dependents = await uow.dependencies.get_dependents("TEST-001")
            assert len(dependents) == 2
            assert "TEST-002" in dependents
            assert "TEST-003" in dependents

    async def test_exists(self, db_path: Path) -> None:
        """Test exists method."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_stories(uow)
            assert await uow.dependencies.exists("TEST-002", "TEST-001") is False

            await uow.dependencies.add("TEST-002", "TEST-001")
            assert await uow.dependencies.exists("TEST-002", "TEST-001") is True

    async def test_get_all_dependencies(self, db_path: Path) -> None:
        """Test getting all dependencies."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_stories(uow)
            await uow.dependencies.add("TEST-002", "TEST-001")
            await uow.dependencies.add("TEST-003", "TEST-001")
            await uow.dependencies.add("TEST-003", "TEST-002")

        async with SQLiteUnitOfWork(db_path) as uow:
            all_deps = await uow.dependencies.get_all_dependencies()
            assert len(all_deps) == 3
            assert ("TEST-002", "TEST-001") in all_deps
            assert ("TEST-003", "TEST-001") in all_deps
            assert ("TEST-003", "TEST-002") in all_deps
