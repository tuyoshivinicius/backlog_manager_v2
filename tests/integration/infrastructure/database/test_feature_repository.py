"""Test SQLite Feature Repository."""

import tempfile
from pathlib import Path

import pytest

from backlog_manager.domain.entities import Feature, Story
from backlog_manager.domain.exceptions import (
    DuplicateWaveException,
    FeatureHasStoriesException,
)
from backlog_manager.domain.value_objects import StoryPoint
from backlog_manager.infrastructure.database import SQLiteUnitOfWork, init_database


@pytest.mark.integration
@pytest.mark.asyncio
class TestFeatureRepository:
    """Test Feature repository operations."""

    @pytest.fixture
    def db_path(self):
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir) / "test.db"

    async def test_add_feature(self, db_path: Path) -> None:
        """Test adding a feature."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            feat_id = await uow.features.add(Feature(name="Auth", wave=1))
            assert feat_id > 0

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.features.get_by_id(feat_id)
            assert result is not None
            assert result.name == "Auth"
            assert result.wave == 1

    async def test_add_duplicate_wave_raises_error(self, db_path: Path) -> None:
        """Test adding feature with duplicate wave raises DuplicateWaveException."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.features.add(Feature(name="Auth", wave=1))

        with pytest.raises(DuplicateWaveException) as exc_info:
            async with SQLiteUnitOfWork(db_path) as uow:
                await uow.features.add(Feature(name="Other", wave=1))

        assert exc_info.value.wave == 1
        assert exc_info.value.existing_feature_name == "Auth"

    async def test_add_duplicate_name_raises_error(self, db_path: Path) -> None:
        """Test adding feature with duplicate name raises ValueError."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.features.add(Feature(name="Auth", wave=1))

        with pytest.raises(ValueError, match="ja existe"):
            async with SQLiteUnitOfWork(db_path) as uow:
                await uow.features.add(Feature(name="Auth", wave=2))

    async def test_get_by_wave(self, db_path: Path) -> None:
        """Test getting feature by wave."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.features.add(Feature(name="Auth", wave=1))
            await uow.features.add(Feature(name="Dashboard", wave=2))

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.features.get_by_wave(2)
            assert result is not None
            assert result.name == "Dashboard"

    async def test_get_by_wave_nonexistent(self, db_path: Path) -> None:
        """Test getting nonexistent wave returns None."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.features.get_by_wave(999)
            assert result is None

    async def test_get_all_ordered_by_wave(self, db_path: Path) -> None:
        """Test get_all returns features ordered by wave."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.features.add(Feature(name="Dashboard", wave=3))
            await uow.features.add(Feature(name="Auth", wave=1))
            await uow.features.add(Feature(name="Reports", wave=2))

        async with SQLiteUnitOfWork(db_path) as uow:
            features = await uow.features.get_all()
            assert len(features) == 3
            assert features[0].wave == 1
            assert features[1].wave == 2
            assert features[2].wave == 3

    async def test_update_feature(self, db_path: Path) -> None:
        """Test updating a feature."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            feat_id = await uow.features.add(Feature(name="Auth", wave=1))

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.features.update(
                Feature(id=feat_id, name="Authentication", wave=1)
            )

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.features.get_by_id(feat_id)
            assert result is not None
            assert result.name == "Authentication"

    async def test_update_to_duplicate_wave_raises_error(self, db_path: Path) -> None:
        """Test updating to existing wave raises DuplicateWaveException."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.features.add(Feature(name="Auth", wave=1))
            feat_id = await uow.features.add(Feature(name="Dashboard", wave=2))

        with pytest.raises(DuplicateWaveException):
            async with SQLiteUnitOfWork(db_path) as uow:
                await uow.features.update(Feature(id=feat_id, name="Dashboard", wave=1))

    async def test_update_nonexistent_raises_error(self, db_path: Path) -> None:
        """Test updating nonexistent feature raises ValueError."""
        await init_database(db_path)

        with pytest.raises(ValueError, match="nao existe"):
            async with SQLiteUnitOfWork(db_path) as uow:
                await uow.features.update(Feature(id=999, name="Test", wave=1))

    async def test_update_none_id_raises_error(self, db_path: Path) -> None:
        """Test updating feature with None id raises ValueError."""
        await init_database(db_path)

        with pytest.raises(ValueError, match="nao existe"):
            async with SQLiteUnitOfWork(db_path) as uow:
                await uow.features.update(Feature(name="Test", wave=1))

    async def test_delete_feature(self, db_path: Path) -> None:
        """Test deleting a feature."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            feat_id = await uow.features.add(Feature(name="Auth", wave=1))

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.features.delete(feat_id)

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.features.get_by_id(feat_id)
            assert result is None

    async def test_delete_feature_with_stories_raises_error(
        self, db_path: Path
    ) -> None:
        """Test deleting feature with stories raises FeatureHasStoriesException."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            feat_id = await uow.features.add(Feature(name="Auth", wave=1))
            await uow.stories.add(
                Story(
                    id="AUTH-001",
                    component="AUTH",
                    name="Login",
                    story_points=StoryPoint.MEDIUM,
                    priority=0,
                    feature_id=feat_id,
                )
            )

        with pytest.raises(FeatureHasStoriesException) as exc_info:
            async with SQLiteUnitOfWork(db_path) as uow:
                await uow.features.delete(feat_id)

        assert exc_info.value.feature_id == feat_id
        assert exc_info.value.story_count == 1

    async def test_delete_nonexistent_raises_error(self, db_path: Path) -> None:
        """Test deleting nonexistent feature raises ValueError."""
        await init_database(db_path)

        with pytest.raises(ValueError, match="nao existe"):
            async with SQLiteUnitOfWork(db_path) as uow:
                await uow.features.delete(999)

    async def test_exists(self, db_path: Path) -> None:
        """Test exists method."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            assert await uow.features.exists(999) is False

            feat_id = await uow.features.add(Feature(name="Auth", wave=1))
            assert await uow.features.exists(feat_id) is True

    async def test_has_stories(self, db_path: Path) -> None:
        """Test has_stories method."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            feat_id = await uow.features.add(Feature(name="Auth", wave=1))
            assert await uow.features.has_stories(feat_id) is False

            await uow.stories.add(
                Story(
                    id="AUTH-001",
                    component="AUTH",
                    name="Login",
                    story_points=StoryPoint.MEDIUM,
                    priority=0,
                    feature_id=feat_id,
                )
            )
            assert await uow.features.has_stories(feat_id) is True

    async def test_get_by_name_returns_feature_when_exists(self, db_path: Path) -> None:
        """Test get_by_name returns feature when it exists."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.features.add(Feature(name="Auth", wave=1))

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.features.get_by_name("Auth")
            assert result is not None
            assert result.name == "Auth"
            assert result.wave == 1

    async def test_get_by_name_returns_none_when_not_exists(
        self, db_path: Path
    ) -> None:
        """Test get_by_name returns None when feature doesn't exist."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.features.get_by_name("NonExistent")
            assert result is None

    async def test_get_by_name_is_case_sensitive(self, db_path: Path) -> None:
        """Test get_by_name is case-sensitive."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.features.add(Feature(name="Auth", wave=1))

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.features.get_by_name("auth")
            assert result is None  # Case-sensitive, so "auth" != "Auth"
