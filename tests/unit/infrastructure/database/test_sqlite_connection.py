"""Tests for SQLite connection management."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from backlog_manager.infrastructure.database.sqlite_connection import (
    create_connection,
    get_database_path,
    init_database,
)


@pytest.mark.unit
class TestGetDatabasePath:
    """Tests for get_database_path function."""

    def test_returns_env_path_when_set(self, tmp_path: Path) -> None:
        """Test that BACKLOG_DB_PATH env var takes priority."""
        env_db = str(tmp_path / "custom.db")
        with patch.dict("os.environ", {"BACKLOG_DB_PATH": env_db}):
            result = get_database_path()
        assert result == Path(env_db)

    def test_returns_default_path_when_env_not_set(self, tmp_path: Path) -> None:
        """Test default path under APPDATA when env var is not set."""
        with (
            patch.dict(
                "os.environ",
                {"APPDATA": str(tmp_path)},
                clear=False,
            ),
            patch.dict("os.environ", {}, clear=False) as env,
        ):
            env.pop("BACKLOG_DB_PATH", None)
            result = get_database_path()

        expected_dir = tmp_path / "BacklogManager" / "data"
        assert result == expected_dir / "backlog.db"
        assert expected_dir.exists()

    def test_creates_data_directory(self, tmp_path: Path) -> None:
        """Test that the data directory is created if it does not exist."""
        with (
            patch.dict(
                "os.environ",
                {"APPDATA": str(tmp_path)},
                clear=False,
            ),
            patch.dict("os.environ", {}, clear=False) as env,
        ):
            env.pop("BACKLOG_DB_PATH", None)
            result = get_database_path()

        data_dir = tmp_path / "BacklogManager" / "data"
        assert data_dir.is_dir()
        assert result.parent == data_dir

    def test_fallback_to_home_when_appdata_not_set(self) -> None:
        """Test fallback to Path.home() when APPDATA is not in env."""
        with (
            patch.dict("os.environ", {}, clear=False) as env,
            patch.object(Path, "home", return_value=Path("/fake/home")),
            patch.object(Path, "mkdir"),
        ):
            env.pop("BACKLOG_DB_PATH", None)
            env.pop("APPDATA", None)
            result = get_database_path()
        assert result == Path("/fake/home") / "BacklogManager" / "data" / "backlog.db"


@pytest.mark.unit
class TestCreateConnection:
    """Tests for create_connection function."""

    @pytest.mark.asyncio
    async def test_uses_get_database_path_when_db_path_is_none(self) -> None:
        """Test that create_connection calls get_database_path when no path given (line 49)."""
        fake_path = Path("/fake/db.sqlite")
        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.row_factory = None

        with (
            patch(
                "backlog_manager.infrastructure.database.sqlite_connection.get_database_path",
                return_value=fake_path,
            ) as mock_get_path,
            patch(
                "backlog_manager.infrastructure.database.sqlite_connection.aiosqlite.connect",
                new_callable=AsyncMock,
                return_value=mock_conn,
            ),
        ):
            conn = await create_connection(None)

        mock_get_path.assert_called_once()
        assert conn is mock_conn

    @pytest.mark.asyncio
    async def test_uses_provided_path(self, tmp_path: Path) -> None:
        """Test that create_connection uses provided path directly."""
        db_path = tmp_path / "test.db"
        conn = await create_connection(db_path)
        try:
            assert conn is not None
        finally:
            await conn.close()

    @pytest.mark.asyncio
    async def test_enables_foreign_keys(self, tmp_path: Path) -> None:
        """Test that PRAGMA foreign_keys is enabled."""
        db_path = tmp_path / "test.db"
        conn = await create_connection(db_path)
        try:
            cursor = await conn.execute("PRAGMA foreign_keys")
            row = await cursor.fetchone()
            assert row[0] == 1
        finally:
            await conn.close()

    @pytest.mark.asyncio
    async def test_row_factory_set(self, tmp_path: Path) -> None:
        """Test that row_factory is set to aiosqlite.Row."""
        import aiosqlite

        db_path = tmp_path / "test.db"
        conn = await create_connection(db_path)
        try:
            assert conn.row_factory is aiosqlite.Row
        finally:
            await conn.close()


@pytest.mark.unit
class TestInitDatabase:
    """Tests for init_database function."""

    @pytest.mark.asyncio
    async def test_init_database_creates_tables(self, tmp_path: Path) -> None:
        """Test that init_database executes schema and creates tables."""
        db_path = tmp_path / "test_init.db"
        await init_database(db_path)

        # Verify database was initialized by connecting and checking tables
        conn = await create_connection(db_path)
        try:
            cursor = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = await cursor.fetchall()
            assert len(tables) > 0
        finally:
            await conn.close()

    @pytest.mark.asyncio
    async def test_init_database_uses_default_path_when_none(self) -> None:
        """Test that init_database calls create_connection with None."""
        mock_conn = AsyncMock()
        mock_conn.executescript = AsyncMock()
        mock_conn.commit = AsyncMock()
        mock_conn.close = AsyncMock()

        with (
            patch(
                "backlog_manager.infrastructure.database.sqlite_connection.create_connection",
                new_callable=AsyncMock,
                return_value=mock_conn,
            ) as mock_create,
            patch(
                "backlog_manager.infrastructure.database.sqlite_connection._SCHEMA_PATH",
            ) as mock_schema_path,
        ):
            mock_schema_path.read_text.return_value = (
                "CREATE TABLE IF NOT EXISTS test (id INTEGER);"
            )
            await init_database(None)

        mock_create.assert_called_once_with(None)
        mock_conn.executescript.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_init_database_closes_connection_on_error(self) -> None:
        """Test that init_database closes connection even if executescript fails."""
        mock_conn = AsyncMock()
        mock_conn.executescript = AsyncMock(side_effect=RuntimeError("schema error"))
        mock_conn.commit = AsyncMock()
        mock_conn.close = AsyncMock()

        with (
            patch(
                "backlog_manager.infrastructure.database.sqlite_connection.create_connection",
                new_callable=AsyncMock,
                return_value=mock_conn,
            ),
            patch(
                "backlog_manager.infrastructure.database.sqlite_connection._SCHEMA_PATH",
            ) as mock_schema_path,
            pytest.raises(RuntimeError, match="schema error"),
        ):
            mock_schema_path.read_text.return_value = "INVALID SQL"
            await init_database(None)

        mock_conn.close.assert_called_once()
