"""Test database constraints."""

import tempfile
from pathlib import Path

import pytest

from backlog_manager.infrastructure.database import create_connection, init_database


@pytest.mark.integration
@pytest.mark.asyncio
class TestConstraints:
    """Test database CHECK constraints."""

    @pytest.fixture
    async def db_connection(self):
        """Create a test database and connection."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = Path(tmp_dir) / "test.db"
            await init_database(db_path)
            conn = await create_connection(db_path)
            try:
                yield conn
            finally:
                await conn.close()

    async def test_story_points_check_constraint(self, db_connection) -> None:
        """Test story_points must be 3, 5, 8, or 13."""
        # Valid values should work
        for points in [3, 5, 8, 13]:
            await db_connection.execute(
                """
                INSERT INTO Story (id, component, name, story_points, priority)
                VALUES (?, 'TEST', 'Test Story', ?, 0)
                """,
                (f"TEST-{points:03d}", points),
            )

        await db_connection.commit()

        # Invalid value should fail
        with pytest.raises(Exception) as exc_info:
            await db_connection.execute(
                """
                INSERT INTO Story (id, component, name, story_points, priority)
                VALUES ('TEST-999', 'TEST', 'Test Story', 7, 0)
                """
            )
        assert "CHECK constraint failed" in str(exc_info.value)

    async def test_priority_check_constraint(self, db_connection) -> None:
        """Test priority must be >= 0."""
        # Valid value should work
        await db_connection.execute(
            """
            INSERT INTO Story (id, component, name, story_points, priority)
            VALUES ('TEST-001', 'TEST', 'Test Story', 5, 0)
            """
        )
        await db_connection.commit()

        # Negative value should fail
        with pytest.raises(Exception) as exc_info:
            await db_connection.execute(
                """
                INSERT INTO Story (id, component, name, story_points, priority)
                VALUES ('TEST-002', 'TEST', 'Test Story', 5, -1)
                """
            )
        assert "CHECK constraint failed" in str(exc_info.value)

    async def test_wave_check_constraint(self, db_connection) -> None:
        """Test wave must be > 0."""
        # Valid value should work
        await db_connection.execute(
            "INSERT INTO Feature (name, wave) VALUES ('Feature 1', 1)"
        )
        await db_connection.commit()

        # Zero should fail
        with pytest.raises(Exception) as exc_info:
            await db_connection.execute(
                "INSERT INTO Feature (name, wave) VALUES ('Feature 0', 0)"
            )
        assert "CHECK constraint failed" in str(exc_info.value)

    async def test_self_dependency_check_constraint(self, db_connection) -> None:
        """Test story cannot depend on itself."""
        # Create a story first
        await db_connection.execute(
            """
            INSERT INTO Story (id, component, name, story_points, priority)
            VALUES ('TEST-001', 'TEST', 'Test Story', 5, 0)
            """
        )
        await db_connection.commit()

        # Self-dependency should fail
        with pytest.raises(Exception) as exc_info:
            await db_connection.execute(
                """
                INSERT INTO Story_Dependency (story_id, depends_on_id)
                VALUES ('TEST-001', 'TEST-001')
                """
            )
        assert "CHECK constraint failed" in str(exc_info.value)

    async def test_feature_name_unique_constraint(self, db_connection) -> None:
        """Test feature name must be unique."""
        await db_connection.execute(
            "INSERT INTO Feature (name, wave) VALUES ('Feature A', 1)"
        )
        await db_connection.commit()

        with pytest.raises(Exception) as exc_info:
            await db_connection.execute(
                "INSERT INTO Feature (name, wave) VALUES ('Feature A', 2)"
            )
        assert "UNIQUE constraint failed" in str(exc_info.value)

    async def test_feature_wave_unique_constraint(self, db_connection) -> None:
        """Test feature wave must be unique."""
        await db_connection.execute(
            "INSERT INTO Feature (name, wave) VALUES ('Feature A', 1)"
        )
        await db_connection.commit()

        with pytest.raises(Exception) as exc_info:
            await db_connection.execute(
                "INSERT INTO Feature (name, wave) VALUES ('Feature B', 1)"
            )
        assert "UNIQUE constraint failed" in str(exc_info.value)
