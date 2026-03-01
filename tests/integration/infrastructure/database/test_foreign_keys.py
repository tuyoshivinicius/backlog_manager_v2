"""Test database foreign key relationships."""

import tempfile
from pathlib import Path

import pytest

from backlog_manager.infrastructure.database import create_connection, init_database


@pytest.mark.integration
@pytest.mark.asyncio
class TestForeignKeys:
    """Test database foreign key constraints."""

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

    async def test_story_developer_fk(self, db_connection) -> None:
        """Test Story.developer_id references Developer."""
        # Create developer
        await db_connection.execute("INSERT INTO Developer (name) VALUES ('John')")

        # Get developer id
        async with db_connection.execute(
            "SELECT id FROM Developer WHERE name = 'John'"
        ) as cursor:
            row = await cursor.fetchone()
            dev_id = row[0]

        # Create story with valid developer_id
        await db_connection.execute(
            """
            INSERT INTO Story (id, component, name, story_points, priority, developer_id)
            VALUES ('TEST-001', 'TEST', 'Test Story', 5, 0, ?)
            """,
            (dev_id,),
        )
        await db_connection.commit()

        # Invalid developer_id should fail
        with pytest.raises(Exception) as exc_info:
            await db_connection.execute(
                """
                INSERT INTO Story (id, component, name, story_points, priority, developer_id)
                VALUES ('TEST-002', 'TEST', 'Test Story 2', 5, 0, 999)
                """
            )
        assert "FOREIGN KEY constraint failed" in str(exc_info.value)

    async def test_story_feature_fk(self, db_connection) -> None:
        """Test Story.feature_id references Feature."""
        # Create feature
        await db_connection.execute(
            "INSERT INTO Feature (name, wave) VALUES ('Feature 1', 1)"
        )

        # Get feature id
        async with db_connection.execute(
            "SELECT id FROM Feature WHERE name = 'Feature 1'"
        ) as cursor:
            row = await cursor.fetchone()
            feat_id = row[0]

        # Create story with valid feature_id
        await db_connection.execute(
            """
            INSERT INTO Story (id, component, name, story_points, priority, feature_id)
            VALUES ('TEST-001', 'TEST', 'Test Story', 5, 0, ?)
            """,
            (feat_id,),
        )
        await db_connection.commit()

        # Invalid feature_id should fail
        with pytest.raises(Exception) as exc_info:
            await db_connection.execute(
                """
                INSERT INTO Story (id, component, name, story_points, priority, feature_id)
                VALUES ('TEST-002', 'TEST', 'Test Story 2', 5, 0, 999)
                """
            )
        assert "FOREIGN KEY constraint failed" in str(exc_info.value)

    async def test_story_dependency_fk(self, db_connection) -> None:
        """Test Story_Dependency references Story."""
        # Create two stories
        await db_connection.execute(
            """
            INSERT INTO Story (id, component, name, story_points, priority)
            VALUES ('TEST-001', 'TEST', 'Test Story 1', 5, 0)
            """
        )
        await db_connection.execute(
            """
            INSERT INTO Story (id, component, name, story_points, priority)
            VALUES ('TEST-002', 'TEST', 'Test Story 2', 5, 1)
            """
        )

        # Valid dependency
        await db_connection.execute(
            """
            INSERT INTO Story_Dependency (story_id, depends_on_id)
            VALUES ('TEST-002', 'TEST-001')
            """
        )
        await db_connection.commit()

        # Invalid story_id should fail
        with pytest.raises(Exception) as exc_info:
            await db_connection.execute(
                """
                INSERT INTO Story_Dependency (story_id, depends_on_id)
                VALUES ('TEST-999', 'TEST-001')
                """
            )
        assert "FOREIGN KEY constraint failed" in str(exc_info.value)

    async def test_developer_delete_set_null(self, db_connection) -> None:
        """Test ON DELETE SET NULL for developer."""
        # Create developer and story
        await db_connection.execute("INSERT INTO Developer (name) VALUES ('John')")

        async with db_connection.execute(
            "SELECT id FROM Developer WHERE name = 'John'"
        ) as cursor:
            row = await cursor.fetchone()
            dev_id = row[0]

        await db_connection.execute(
            """
            INSERT INTO Story (id, component, name, story_points, priority, developer_id)
            VALUES ('TEST-001', 'TEST', 'Test Story', 5, 0, ?)
            """,
            (dev_id,),
        )
        await db_connection.commit()

        # Delete developer
        await db_connection.execute("DELETE FROM Developer WHERE id = ?", (dev_id,))
        await db_connection.commit()

        # Story should still exist with NULL developer_id
        async with db_connection.execute(
            "SELECT developer_id FROM Story WHERE id = 'TEST-001'"
        ) as cursor:
            row = await cursor.fetchone()
            assert row[0] is None

    async def test_story_delete_cascades_dependencies(self, db_connection) -> None:
        """Test ON DELETE CASCADE for story dependencies."""
        # Create stories and dependency
        await db_connection.execute(
            """
            INSERT INTO Story (id, component, name, story_points, priority)
            VALUES ('TEST-001', 'TEST', 'Test Story 1', 5, 0)
            """
        )
        await db_connection.execute(
            """
            INSERT INTO Story (id, component, name, story_points, priority)
            VALUES ('TEST-002', 'TEST', 'Test Story 2', 5, 1)
            """
        )
        await db_connection.execute(
            """
            INSERT INTO Story_Dependency (story_id, depends_on_id)
            VALUES ('TEST-002', 'TEST-001')
            """
        )
        await db_connection.commit()

        # Delete story
        await db_connection.execute("DELETE FROM Story WHERE id = 'TEST-001'")
        await db_connection.commit()

        # Dependency should be deleted
        async with db_connection.execute(
            "SELECT COUNT(*) FROM Story_Dependency"
        ) as cursor:
            row = await cursor.fetchone()
            assert row[0] == 0
