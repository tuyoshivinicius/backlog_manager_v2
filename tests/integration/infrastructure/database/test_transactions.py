"""Test database transactions."""

import tempfile
from pathlib import Path

import pytest
from backlog_manager.domain.entities import Developer, Story
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus
from backlog_manager.infrastructure.database import SQLiteUnitOfWork, init_database


@pytest.mark.integration
@pytest.mark.asyncio
class TestTransactions:
    """Test database transaction handling."""

    @pytest.fixture
    def db_path(self):
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir) / "test.db"

    async def test_commit_on_success(self, db_path: Path) -> None:
        """Test transaction commits on successful exit."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.developers.add(Developer(name="John"))

        # Verify data persisted
        async with SQLiteUnitOfWork(db_path) as uow:
            developers = await uow.developers.get_all()
            assert len(developers) == 1
            assert developers[0].name == "John"

    async def test_rollback_on_exception(self, db_path: Path) -> None:
        """Test transaction rollback on exception."""
        await init_database(db_path)

        with pytest.raises(ValueError):
            async with SQLiteUnitOfWork(db_path) as uow:
                await uow.developers.add(Developer(name="John"))
                raise ValueError("Simulated error")

        # Verify data was not persisted
        async with SQLiteUnitOfWork(db_path) as uow:
            developers = await uow.developers.get_all()
            assert len(developers) == 0

    async def test_explicit_rollback(self, db_path: Path) -> None:
        """Test explicit rollback reverts changes."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.developers.add(Developer(name="John"))
            await uow.rollback()
            # Manually commit empty transaction
            await uow.commit()

        # Verify data was not persisted
        async with SQLiteUnitOfWork(db_path) as uow:
            developers = await uow.developers.get_all()
            assert len(developers) == 0

    async def test_multiple_operations_in_transaction(self, db_path: Path) -> None:
        """Test multiple operations in single transaction."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            dev_id = await uow.developers.add(Developer(name="John"))

            story = Story(
                id="TEST-001",
                component="TEST",
                name="Test Story",
                story_points=StoryPoint.MEDIUM,
                priority=0,
                status=StoryStatus.BACKLOG,
                developer_id=dev_id,
            )
            await uow.stories.add(story)

        # Verify all data persisted
        async with SQLiteUnitOfWork(db_path) as uow:
            developers = await uow.developers.get_all()
            stories = await uow.stories.get_all()

            assert len(developers) == 1
            assert len(stories) == 1
            assert stories[0].developer_id == developers[0].id

    async def test_partial_failure_rollback(self, db_path: Path) -> None:
        """Test partial failure rolls back all changes."""
        await init_database(db_path)

        with pytest.raises(ValueError):
            async with SQLiteUnitOfWork(db_path) as uow:
                await uow.developers.add(Developer(name="John"))

                # This should fail - duplicate ID
                await uow.stories.add(
                    Story(
                        id="TEST-001",
                        component="TEST",
                        name="Story 1",
                        story_points=StoryPoint.SMALL,
                        priority=0,
                    )
                )
                await uow.stories.add(
                    Story(
                        id="TEST-001",  # Duplicate
                        component="TEST",
                        name="Story 2",
                        story_points=StoryPoint.SMALL,
                        priority=1,
                    )
                )

        # Verify nothing persisted
        async with SQLiteUnitOfWork(db_path) as uow:
            developers = await uow.developers.get_all()
            stories = await uow.stories.get_all()

            assert len(developers) == 0
            assert len(stories) == 0

    async def test_context_manager_required(self, db_path: Path) -> None:
        """Test that repositories require context manager."""
        await init_database(db_path)

        uow = SQLiteUnitOfWork(db_path)

        with pytest.raises(RuntimeError, match="context manager"):
            _ = uow.stories

        with pytest.raises(RuntimeError, match="context manager"):
            _ = uow.developers

        with pytest.raises(RuntimeError, match="context manager"):
            _ = uow.features

        with pytest.raises(RuntimeError, match="context manager"):
            _ = uow.dependencies
