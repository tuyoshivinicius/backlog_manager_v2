"""Test database schema creation."""

import tempfile
from pathlib import Path

import pytest
from backlog_manager.infrastructure.database import create_connection, init_database


@pytest.mark.integration
@pytest.mark.asyncio
class TestSchema:
    """Test database schema initialization."""

    async def test_init_database_creates_tables(self) -> None:
        """Test that init_database creates all required tables."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test.db"
            await init_database(db_path)

            conn = await create_connection(db_path)
            try:
                # Check tables exist
                async with conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                ) as cursor:
                    tables = [row[0] for row in await cursor.fetchall()]

                assert "Developer" in tables
                assert "Feature" in tables
                assert "Story" in tables
                assert "Story_Dependency" in tables
            finally:
                await conn.close()

    async def test_init_database_creates_indexes(self) -> None:
        """Test that init_database creates all required indexes."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test.db"
            await init_database(db_path)

            conn = await create_connection(db_path)
            try:
                async with conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='index'"
                ) as cursor:
                    indexes = [row[0] for row in await cursor.fetchall()]

                assert "idx_story_status" in indexes
                assert "idx_story_developer" in indexes
                assert "idx_story_feature" in indexes
                assert "idx_story_priority" in indexes
            finally:
                await conn.close()

    async def test_init_database_idempotent(self) -> None:
        """Test that init_database can be called multiple times."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test.db"

            # Call twice - should not raise
            await init_database(db_path)
            await init_database(db_path)

            # Verify tables still exist
            conn = await create_connection(db_path)
            try:
                async with conn.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
                ) as cursor:
                    row = await cursor.fetchone()
                    assert row[0] >= 4
            finally:
                await conn.close()

    async def test_foreign_keys_enabled(self) -> None:
        """Test that foreign keys are enabled on connection."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test.db"
            await init_database(db_path)

            conn = await create_connection(db_path)
            try:
                async with conn.execute("PRAGMA foreign_keys") as cursor:
                    row = await cursor.fetchone()
                    assert row[0] == 1  # 1 = ON
            finally:
                await conn.close()
