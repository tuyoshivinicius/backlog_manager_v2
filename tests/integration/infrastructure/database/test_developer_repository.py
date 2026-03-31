"""Test SQLite Developer Repository."""

import tempfile
from pathlib import Path

import pytest
from backlog_manager.domain.entities import Developer
from backlog_manager.infrastructure.database import SQLiteUnitOfWork, init_database


@pytest.mark.integration
@pytest.mark.asyncio
class TestDeveloperRepository:
    """Test Developer repository operations."""

    @pytest.fixture
    def db_path(self):
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir) / "test.db"

    async def test_add_developer(self, db_path: Path) -> None:
        """Test adding a developer."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            dev_id = await uow.developers.add(Developer(name="John Doe"))
            assert dev_id > 0

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.developers.get_by_id(dev_id)
            assert result is not None
            assert result.name == "John Doe"
            assert result.id == dev_id

    async def test_get_all_ordered_by_name(self, db_path: Path) -> None:
        """Test get_all returns developers ordered by name."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.developers.add(Developer(name="Charlie"))
            await uow.developers.add(Developer(name="Alice"))
            await uow.developers.add(Developer(name="Bob"))

        async with SQLiteUnitOfWork(db_path) as uow:
            devs = await uow.developers.get_all()
            assert len(devs) == 3
            assert devs[0].name == "Alice"
            assert devs[1].name == "Bob"
            assert devs[2].name == "Charlie"

    async def test_update_developer(self, db_path: Path) -> None:
        """Test updating a developer."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            dev_id = await uow.developers.add(Developer(name="John"))

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.developers.update(Developer(id=dev_id, name="Jane"))

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.developers.get_by_id(dev_id)
            assert result is not None
            assert result.name == "Jane"

    async def test_update_nonexistent_raises_error(self, db_path: Path) -> None:
        """Test updating nonexistent developer raises ValueError."""
        await init_database(db_path)

        with pytest.raises(ValueError, match="nao existe"):
            async with SQLiteUnitOfWork(db_path) as uow:
                await uow.developers.update(Developer(id=999, name="Test"))

    async def test_update_none_id_raises_error(self, db_path: Path) -> None:
        """Test updating developer with None id raises ValueError."""
        await init_database(db_path)

        with pytest.raises(ValueError, match="nao existe"):
            async with SQLiteUnitOfWork(db_path) as uow:
                await uow.developers.update(Developer(name="Test"))

    async def test_delete_developer(self, db_path: Path) -> None:
        """Test deleting a developer."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            dev_id = await uow.developers.add(Developer(name="John"))

        async with SQLiteUnitOfWork(db_path) as uow:
            await uow.developers.delete(dev_id)

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.developers.get_by_id(dev_id)
            assert result is None

    async def test_delete_nonexistent_raises_error(self, db_path: Path) -> None:
        """Test deleting nonexistent developer raises ValueError."""
        await init_database(db_path)

        with pytest.raises(ValueError, match="nao existe"):
            async with SQLiteUnitOfWork(db_path) as uow:
                await uow.developers.delete(999)

    async def test_exists(self, db_path: Path) -> None:
        """Test exists method."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            assert await uow.developers.exists(999) is False

            dev_id = await uow.developers.add(Developer(name="John"))
            assert await uow.developers.exists(dev_id) is True

    async def test_get_nonexistent(self, db_path: Path) -> None:
        """Test getting nonexistent developer returns None."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            result = await uow.developers.get_by_id(999)
            assert result is None
