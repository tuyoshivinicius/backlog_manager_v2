"""Test SQLite Story Repository."""

import tempfile
from pathlib import Path

import pytest

from backlog_manager.domain.entities import Developer, Feature, Story
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus
from backlog_manager.infrastructure.database import SQLiteUnitOfWork, init_database


@pytest.mark.integration
@pytest.mark.asyncio
class TestStoryRepository:
    """Test Story repository operations."""

    @pytest.fixture
    def db_path(self):
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir) / "test.db"

    async def test_add_story(self, db_path: Path) -> None:
        """Test adding a story."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            story = Story(
                id="AUTH-001",
                component="AUTH",
                name="Implement login",
                story_points=StoryPoint.MEDIUM,
                priority=0,
            )
            await uow.stories.add(story)

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.stories.get_by_id("AUTH-001")
            assert result is not None
            assert result.id == "AUTH-001"
            assert result.name == "Implement login"

    async def test_add_duplicate_raises_error(self, db_path: Path) -> None:
        """Test adding duplicate story raises ValueError."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            story = Story(
                id="AUTH-001",
                component="AUTH",
                name="Implement login",
                story_points=StoryPoint.MEDIUM,
                priority=0,
            )
            await uow.stories.add(story)

        with pytest.raises(ValueError, match="ja existe"):
            async with SQLiteUnitOfWork(db_path) as uow:
                await uow.stories.add(story)

    async def test_get_all_ordered_by_priority(self, db_path: Path) -> None:
        """Test get_all returns stories ordered by priority."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.stories.add(
                Story(
                    id="AUTH-003",
                    component="AUTH",
                    name="Story 3",
                    story_points=StoryPoint.SMALL,
                    priority=2,
                )
            )
            await uow.stories.add(
                Story(
                    id="AUTH-001",
                    component="AUTH",
                    name="Story 1",
                    story_points=StoryPoint.SMALL,
                    priority=0,
                )
            )
            await uow.stories.add(
                Story(
                    id="AUTH-002",
                    component="AUTH",
                    name="Story 2",
                    story_points=StoryPoint.SMALL,
                    priority=1,
                )
            )

        async with SQLiteUnitOfWork(db_path) as uow:
            stories = await uow.stories.get_all()
            assert len(stories) == 3
            assert stories[0].id == "AUTH-001"
            assert stories[1].id == "AUTH-002"
            assert stories[2].id == "AUTH-003"

    async def test_get_by_status(self, db_path: Path) -> None:
        """Test filtering stories by status."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.stories.add(
                Story(
                    id="AUTH-001",
                    component="AUTH",
                    name="Story 1",
                    story_points=StoryPoint.SMALL,
                    priority=0,
                    status=StoryStatus.BACKLOG,
                )
            )
            await uow.stories.add(
                Story(
                    id="AUTH-002",
                    component="AUTH",
                    name="Story 2",
                    story_points=StoryPoint.SMALL,
                    priority=1,
                    status=StoryStatus.IN_PROGRESS,
                )
            )

        async with SQLiteUnitOfWork(db_path) as uow:
            backlog = await uow.stories.get_by_status("BACKLOG")
            assert len(backlog) == 1
            assert backlog[0].id == "AUTH-001"

    async def test_get_by_developer(self, db_path: Path) -> None:
        """Test filtering stories by developer."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            dev_id = await uow.developers.add(Developer(name="John"))
            await uow.stories.add(
                Story(
                    id="AUTH-001",
                    component="AUTH",
                    name="Story 1",
                    story_points=StoryPoint.SMALL,
                    priority=0,
                    developer_id=dev_id,
                )
            )
            await uow.stories.add(
                Story(
                    id="AUTH-002",
                    component="AUTH",
                    name="Story 2",
                    story_points=StoryPoint.SMALL,
                    priority=1,
                )
            )

        async with SQLiteUnitOfWork(db_path) as uow:
            dev_stories = await uow.stories.get_by_developer(dev_id)
            assert len(dev_stories) == 1
            assert dev_stories[0].id == "AUTH-001"

    async def test_get_by_feature(self, db_path: Path) -> None:
        """Test filtering stories by feature."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            feat_id = await uow.features.add(Feature(name="Auth", wave=1))
            await uow.stories.add(
                Story(
                    id="AUTH-001",
                    component="AUTH",
                    name="Story 1",
                    story_points=StoryPoint.SMALL,
                    priority=0,
                    feature_id=feat_id,
                )
            )

        async with SQLiteUnitOfWork(db_path) as uow:
            feat_stories = await uow.stories.get_by_feature(feat_id)
            assert len(feat_stories) == 1
            assert feat_stories[0].id == "AUTH-001"

    async def test_update_story(self, db_path: Path) -> None:
        """Test updating a story."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.stories.add(
                Story(
                    id="AUTH-001",
                    component="AUTH",
                    name="Original Name",
                    story_points=StoryPoint.SMALL,
                    priority=0,
                )
            )

        async with SQLiteUnitOfWork(db_path) as uow:
            story = await uow.stories.get_by_id("AUTH-001")
            assert story is not None
            updated = Story(
                id=story.id,
                component=story.component,
                name="Updated Name",
                story_points=StoryPoint.LARGE,
                priority=5,
                status=StoryStatus.IN_PROGRESS,
            )
            await uow.stories.update(updated)

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.stories.get_by_id("AUTH-001")
            assert result is not None
            assert result.name == "Updated Name"
            assert result.story_points == StoryPoint.LARGE
            assert result.priority == 5

    async def test_update_nonexistent_raises_error(self, db_path: Path) -> None:
        """Test updating nonexistent story raises ValueError."""
        await init_database(db_path)

        with pytest.raises(ValueError, match="nao existe"):
            async with SQLiteUnitOfWork(db_path) as uow:
                await uow.stories.update(
                    Story(
                        id="AUTH-999",
                        component="AUTH",
                        name="Test",
                        story_points=StoryPoint.SMALL,
                        priority=0,
                    )
                )

    async def test_delete_story(self, db_path: Path) -> None:
        """Test deleting a story."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.stories.add(
                Story(
                    id="AUTH-001",
                    component="AUTH",
                    name="Test",
                    story_points=StoryPoint.SMALL,
                    priority=0,
                )
            )

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.stories.delete("AUTH-001")

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.stories.get_by_id("AUTH-001")
            assert result is None

    async def test_delete_nonexistent_raises_error(self, db_path: Path) -> None:
        """Test deleting nonexistent story raises ValueError."""
        await init_database(db_path)

        with pytest.raises(ValueError, match="nao existe"):
            async with SQLiteUnitOfWork(db_path) as uow:
                await uow.stories.delete("AUTH-999")

    async def test_exists(self, db_path: Path) -> None:
        """Test exists method."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            assert await uow.stories.exists("AUTH-001") is False

            await uow.stories.add(
                Story(
                    id="AUTH-001",
                    component="AUTH",
                    name="Test",
                    story_points=StoryPoint.SMALL,
                    priority=0,
                )
            )

            assert await uow.stories.exists("AUTH-001") is True
