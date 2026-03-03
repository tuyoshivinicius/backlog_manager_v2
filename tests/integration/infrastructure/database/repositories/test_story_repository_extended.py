"""Integration tests for StoryRepository extensions (EP-003)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from backlog_manager.domain.entities import Story
from backlog_manager.domain.value_objects import StoryPoint
from backlog_manager.infrastructure.database import SQLiteUnitOfWork, init_database


@pytest.mark.integration
@pytest.mark.asyncio
class TestGetMaxIdNumber:
    """Tests for get_max_id_number method."""

    @pytest.fixture
    def db_path(self):
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir) / "test.db"

    async def test_returns_zero_when_no_stories(self, db_path: Path):
        """Should return 0 when no stories exist for component."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.stories.get_max_id_number("AUTH")
            assert result == 0

    async def test_returns_max_number_for_component(self, db_path: Path):
        """Should return max number for existing component."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            story1 = Story(
                id="AUTH-001",
                component="AUTH",
                name="Story 1",
                story_points=StoryPoint.SMALL,
                priority=1,
            )
            story2 = Story(
                id="AUTH-005",
                component="AUTH",
                name="Story 2",
                story_points=StoryPoint.MEDIUM,
                priority=2,
            )
            await uow.stories.add(story1)
            await uow.stories.add(story2)

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.stories.get_max_id_number("AUTH")
            assert result == 5

    async def test_is_case_insensitive(self, db_path: Path):
        """Should match component case-insensitively."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            story = Story(
                id="AUTH-003",
                component="AUTH",
                name="Story",
                story_points=StoryPoint.SMALL,
                priority=1,
            )
            await uow.stories.add(story)

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.stories.get_max_id_number("auth")
            assert result == 3

    async def test_isolates_components(self, db_path: Path):
        """Should return max for specific component only."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            story1 = Story(
                id="AUTH-010",
                component="AUTH",
                name="Auth Story",
                story_points=StoryPoint.SMALL,
                priority=1,
            )
            story2 = Story(
                id="CORE-005",
                component="CORE",
                name="Core Story",
                story_points=StoryPoint.MEDIUM,
                priority=2,
            )
            await uow.stories.add(story1)
            await uow.stories.add(story2)

        async with SQLiteUnitOfWork(db_path) as uow:
            assert await uow.stories.get_max_id_number("AUTH") == 10
            assert await uow.stories.get_max_id_number("CORE") == 5


@pytest.mark.integration
@pytest.mark.asyncio
class TestGetMaxPriority:
    """Tests for get_max_priority method."""

    @pytest.fixture
    def db_path(self):
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir) / "test.db"

    async def test_returns_zero_when_empty(self, db_path: Path):
        """Should return 0 when no stories exist."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.stories.get_max_priority()
            assert result == 0

    async def test_returns_max_priority(self, db_path: Path):
        """Should return highest priority value."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
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
                priority=5,
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

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.stories.get_max_priority()
            assert result == 5


@pytest.mark.integration
@pytest.mark.asyncio
class TestGetByPriority:
    """Tests for get_by_priority method."""

    @pytest.fixture
    def db_path(self):
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir) / "test.db"

    async def test_returns_none_when_not_found(self, db_path: Path):
        """Should return None when no story has the priority."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.stories.get_by_priority(1)
            assert result is None

    async def test_returns_story_with_exact_priority(self, db_path: Path):
        """Should return story with exact priority match."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            story = Story(
                id="AUTH-001",
                component="AUTH",
                name="Test Story",
                story_points=StoryPoint.SMALL,
                priority=3,
            )
            await uow.stories.add(story)

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.stories.get_by_priority(3)
            assert result is not None
            assert result.id == "AUTH-001"
            assert result.priority == 3

    async def test_returns_correct_story_among_multiple(self, db_path: Path):
        """Should return correct story when multiple exist."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
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
            await uow.stories.add(story1)
            await uow.stories.add(story2)

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.stories.get_by_priority(2)
            assert result is not None
            assert result.id == "AUTH-002"
