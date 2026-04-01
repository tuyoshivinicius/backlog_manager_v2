"""Pytest configuration and fixtures.

This module provides shared fixtures for all tests, including
async fixtures and pytest-qt integration with qasync.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Generator
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from backlog_manager.application.dto.developer import CreateDeveloperInputDTO
from backlog_manager.application.dto.feature import CreateFeatureInputDTO
from backlog_manager.application.dto.story import CreateStoryInputDTO, StoryOutputDTO
from backlog_manager.infrastructure.database.sqlite_connection import create_connection
from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork
from backlog_manager.presentation.container import DIContainer

if TYPE_CHECKING:
    import aiosqlite

# ============================================================================
# Database Fixtures
# ============================================================================


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Create a temporary database path.

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Returns:
        Path to temporary database file.
    """
    return tmp_path / "test_backlog.db"


@pytest_asyncio.fixture
async def db_connection(
    temp_db_path: Path,
) -> AsyncGenerator[aiosqlite.Connection, None]:
    """Create a database connection with schema initialized.

    Args:
        temp_db_path: Temporary database path fixture.

    Yields:
        Initialized database connection.
    """
    conn = await create_connection(temp_db_path)
    try:
        yield conn
    finally:
        await conn.close()


@pytest_asyncio.fixture
async def uow(temp_db_path: Path) -> AsyncGenerator[SQLiteUnitOfWork, None]:
    """Create a Unit of Work for testing.

    Args:
        temp_db_path: Temporary database path fixture.

    Yields:
        SQLiteUnitOfWork instance in context.
    """
    async with SQLiteUnitOfWork(temp_db_path) as unit_of_work:
        yield unit_of_work


# ============================================================================
# DI Container Fixtures
# ============================================================================


@pytest.fixture
def container(temp_db_path: Path) -> Generator[DIContainer, None, None]:
    """Create a DIContainer for testing.

    Args:
        temp_db_path: Temporary database path fixture.

    Yields:
        Initialized DIContainer.
    """
    # Reset any existing instance
    DIContainer.reset()
    container = DIContainer.initialize(temp_db_path)
    try:
        yield container
    finally:
        DIContainer.reset()


# ============================================================================
# Sample Data Fixtures
# ============================================================================


@pytest.fixture
def sample_story_dto() -> StoryOutputDTO:
    """Create a sample story DTO for testing.

    Returns:
        Sample StoryOutputDTO.
    """
    return StoryOutputDTO(
        id="COMP-001",
        component="COMP",
        name="Sample Story",
        story_points=5,
        priority=1,
        status="BACKLOG",
        duration=3,
        start_date=date(2026, 1, 15),
        end_date=date(2026, 1, 17),
        developer_id=1,
        feature_id=1,
    )


@pytest.fixture
def sample_stories() -> list[StoryOutputDTO]:
    """Create a list of sample stories for testing.

    Returns:
        List of sample StoryOutputDTOs.
    """
    return [
        StoryOutputDTO(
            id="COMP-001",
            component="COMP",
            name="Primeira Historia",
            story_points=3,
            priority=1,
            status="BACKLOG",
            duration=2,
            start_date=date(2026, 1, 15),
            end_date=date(2026, 1, 16),
            developer_id=1,
            feature_id=1,
            developer_name="Joao Silva",
            feature_name="Feature Alpha",
            wave=1,
            dependency_ids=["API-001"],
        ),
        StoryOutputDTO(
            id="COMP-002",
            component="COMP",
            name="Segunda Historia",
            story_points=5,
            priority=2,
            status="BACKLOG",
            duration=3,
            start_date=date(2026, 1, 17),
            end_date=date(2026, 1, 20),
            developer_id=None,
            feature_id=1,
            developer_name=None,
            feature_name="Feature Alpha",
            wave=1,
            dependency_ids=[],
        ),
        StoryOutputDTO(
            id="API-001",
            component="API",
            name="Terceira Historia",
            story_points=8,
            priority=3,
            status="DOING",
            duration=4,
            start_date=None,
            end_date=None,
            developer_id=2,
            feature_id=None,
            developer_name="Maria Santos",
            feature_name=None,
            wave=0,
            dependency_ids=[],
        ),
    ]


@pytest.fixture
def create_story_input() -> CreateStoryInputDTO:
    """Create a sample create story input DTO.

    Returns:
        Sample CreateStoryInputDTO.
    """
    return CreateStoryInputDTO(
        component="TEST",
        name="Test Story",
        story_points=5,
        feature_id=None,
    )


@pytest.fixture
def create_developer_input() -> CreateDeveloperInputDTO:
    """Create a sample create developer input DTO.

    Returns:
        Sample CreateDeveloperInputDTO.
    """
    return CreateDeveloperInputDTO(name="Test Developer")


@pytest.fixture
def create_feature_input() -> CreateFeatureInputDTO:
    """Create a sample create feature input DTO.

    Returns:
        Sample CreateFeatureInputDTO.
    """
    return CreateFeatureInputDTO(name="Test Feature", wave=1)


# ============================================================================
# Headless Mock Infrastructure
# ============================================================================


class MockQBase:
    """Mock base class for QObject, QAbstractTableModel, QSortFilterProxyModel.

    Accepts any arguments in __init__ to mimic Qt base classes.
    """

    def __init__(self, *args, **kwargs):
        """Stub intencional: simula interface para testes headless."""


class MockSignal:
    """Mock for PySide6 Signal that records emissions."""

    def __init__(self, *args):
        self.emissions = []

    def emit(self, *args):
        self.emissions.append(args)

    def connect(self, slot):
        """Stub intencional: simula interface para testes headless."""

    def disconnect(self, slot=None):
        """Stub intencional: simula interface para testes headless."""


@pytest.fixture
def mock_signal():
    """Provide a MockSignal instance for headless ViewModel tests."""
    return MockSignal


def _create_pyside6_mock_modules():
    """Create a dictionary of mock PySide6 modules for sys.modules patching.

    Returns:
        dict suitable for use with patch.dict("sys.modules", ...).
    """
    from unittest.mock import MagicMock

    mock_qt_core = MagicMock()
    mock_qt_core.Signal = MockSignal
    mock_qt_core.QObject = object

    return {
        "PySide6": MagicMock(),
        "PySide6.QtCore": mock_qt_core,
        "PySide6.QtWidgets": MagicMock(),
        "PySide6.QtGui": MagicMock(),
    }


@pytest.fixture
def pyside6_mock():
    """Provide mock PySide6 modules dict for headless tests.

    Usage in tests:
        def test_something(pyside6_mock):
            with patch.dict("sys.modules", pyside6_mock):
                from backlog_manager.presentation.viewmodels.xxx import XxxViewModel
    """
    return _create_pyside6_mock_modules()


# ============================================================================
# Helper Functions
# ============================================================================


def run_async(coro, loop: asyncio.AbstractEventLoop | None = None):  # type: ignore[no-untyped-def]
    """Run an async coroutine in the given event loop.

    Args:
        coro: Coroutine to run.
        loop: Event loop to use (defaults to current loop).

    Returns:
        Result of the coroutine.
    """
    if loop is None:
        loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)
