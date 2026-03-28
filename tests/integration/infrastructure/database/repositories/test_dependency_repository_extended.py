"""Integration tests for StoryDependencyRepository extensions (EP-003)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from backlog_manager.domain.entities import Story
from backlog_manager.domain.value_objects import StoryPoint
from backlog_manager.infrastructure.database import SQLiteUnitOfWork, init_database


@pytest.mark.integration
@pytest.mark.asyncio
class TestRemoveAllForStory:
    """Tests for remove_all_for_story method."""

    @pytest.fixture
    def db_path(self):
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir) / "test.db"

    async def _create_stories(self, uow):
        """Helper to create test stories."""
        story1 = Story(
            id="AUTH-001",
            component="AUTH",
            name="Story 1",
            story_points=StoryPoint.SMALL,
            priority=1,
        )
        story2 = Story(
            id="AUTH-002",
            component="AUTH",
            name="Story 2",
            story_points=StoryPoint.MEDIUM,
            priority=2,
        )
        story3 = Story(
            id="AUTH-003",
            component="AUTH",
            name="Story 3",
            story_points=StoryPoint.LARGE,
            priority=3,
        )
        await uow.stories.add(story1)
        await uow.stories.add(story2)
        await uow.stories.add(story3)

    async def test_removes_dependencies_where_story_is_dependent(self, db_path: Path):
        """Should remove dependencies where story_id is the dependent."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_stories(uow)
            await uow.dependencies.add("AUTH-001", "AUTH-002")
            await uow.dependencies.add("AUTH-001", "AUTH-003")

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.dependencies.remove_all_for_story("AUTH-001")

        async with SQLiteUnitOfWork(db_path) as uow:
            deps = await uow.dependencies.get_dependencies("AUTH-001")
            assert len(deps) == 0

    async def test_removes_dependencies_where_story_is_dependency(self, db_path: Path):
        """Should remove dependencies where story_id is the dependency."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_stories(uow)
            await uow.dependencies.add("AUTH-002", "AUTH-001")
            await uow.dependencies.add("AUTH-003", "AUTH-001")

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.dependencies.remove_all_for_story("AUTH-001")

        async with SQLiteUnitOfWork(db_path) as uow:
            deps2 = await uow.dependencies.get_dependencies("AUTH-002")
            deps3 = await uow.dependencies.get_dependencies("AUTH-003")
            assert len(deps2) == 0
            assert len(deps3) == 0

    async def test_removes_both_directions(self, db_path: Path):
        """Should remove all dependencies in both directions."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_stories(uow)
            await uow.dependencies.add("AUTH-001", "AUTH-002")
            await uow.dependencies.add("AUTH-003", "AUTH-001")

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.dependencies.remove_all_for_story("AUTH-001")

        async with SQLiteUnitOfWork(db_path) as uow:
            all_deps = await uow.dependencies.get_all_dependencies()
            assert len(all_deps) == 0

    async def test_leaves_other_dependencies_intact(self, db_path: Path):
        """Should not affect dependencies not involving the story."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_stories(uow)
            await uow.dependencies.add("AUTH-001", "AUTH-002")
            await uow.dependencies.add("AUTH-002", "AUTH-003")

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.dependencies.remove_all_for_story("AUTH-001")

        async with SQLiteUnitOfWork(db_path) as uow:
            deps = await uow.dependencies.get_dependencies("AUTH-002")
            assert "AUTH-003" in deps

    async def test_idempotent_when_no_dependencies(self, db_path: Path):
        """Should not raise when story has no dependencies."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await self._create_stories(uow)

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.dependencies.remove_all_for_story("AUTH-001")

        async with SQLiteUnitOfWork(db_path) as uow:
            all_deps = await uow.dependencies.get_all_dependencies()
            assert len(all_deps) == 0
