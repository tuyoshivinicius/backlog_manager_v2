"""E2E test fixtures and configuration.

This module provides fixtures for end-to-end testing with pytest-qt and qasync,
enabling full integration testing of the GUI with async operations.

Test Isolation Strategy (FR-103):
- Each test receives a fresh temporary database via temp_db_path
- DIContainer is reset before and after each test
- QApplication is managed by pytest-qt's session-scoped qapp fixture
- qasync_loop provides asyncio integration with Qt event loop
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, AsyncGenerator

import pytest
import pytest_asyncio
from PySide6.QtCore import QTimer

from backlog_manager.domain.entities.developer import Developer
from backlog_manager.domain.entities.feature import Feature
from backlog_manager.domain.entities.story import Story
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus
from backlog_manager.infrastructure.database.sqlite_connection import init_database
from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork
from backlog_manager.presentation.container import DIContainer

if TYPE_CHECKING:
    from qasync import QEventLoop

    from backlog_manager.presentation.views.main_window import MainWindow

pytestmark = [pytest.mark.e2e]


# ============================================================================
# Qt/Async Integration Fixtures (T004-T006)
# ============================================================================


@pytest.fixture
def qasync_loop(qapp) -> QEventLoop:
    """Create asyncio event loop integrated with Qt.

    This fixture creates a QEventLoop from qasync that integrates
    Qt's event loop with asyncio, allowing async operations in tests.

    Args:
        qapp: pytest-qt's QApplication fixture (session-scoped).

    Yields:
        Event loop for async E2E tests.

    Note:
        The loop is closed after each test to prevent event loop leaks.
    """
    from qasync import QEventLoop

    loop = QEventLoop(qapp)
    asyncio.set_event_loop(loop)
    yield loop
    # Cleanup: close the loop
    loop.close()


@pytest.fixture
def e2e_app(qasync_loop: QEventLoop, temp_db_path: Path) -> DIContainer:
    """Create DIContainer configured for E2E testing.

    This fixture initializes the DI container with a temporary database,
    ensuring complete isolation between tests.

    Args:
        qasync_loop: The qasync event loop fixture.
        temp_db_path: Temporary database path fixture.

    Yields:
        Initialized DIContainer instance.

    Note:
        DIContainer is reset after each test for proper isolation.
    """
    # Initialize database schema before creating container
    qasync_loop.run_until_complete(init_database(temp_db_path))

    DIContainer.reset()
    container = DIContainer.initialize(temp_db_path)
    yield container
    # Teardown: reset container state (FR-101, FR-102)
    DIContainer.reset()


@pytest.fixture
def e2e_main_window(
    qasync_loop: QEventLoop,
    e2e_app: DIContainer,
    qtbot,  # type: ignore[no-untyped-def]
) -> MainWindow:
    """Create MainWindow configured for E2E testing.

    This fixture creates the main window with full DI integration,
    registering it with qtbot for automatic cleanup.

    Args:
        qasync_loop: The qasync event loop fixture.
        e2e_app: The DIContainer fixture.
        qtbot: pytest-qt's qtbot fixture.

    Yields:
        MainWindow instance ready for testing.

    Note:
        Window is shown and events are processed before yielding.
    """
    from backlog_manager.presentation.views.main_window import MainWindow

    viewmodel = e2e_app.main_window_viewmodel
    window = MainWindow(viewmodel)
    qtbot.addWidget(window)
    window.show()

    # Process pending Qt events using QApplication
    from PySide6.QtWidgets import QApplication

    QApplication.processEvents()

    yield window

    # Teardown
    window.close()


# ============================================================================
# Database Fixtures (T007)
# ============================================================================


@pytest_asyncio.fixture
async def e2e_populated_db(
    e2e_app: DIContainer,
) -> AsyncGenerator[SQLiteUnitOfWork, None]:
    """Create database populated with standard test data.

    This fixture populates the database with a standard set of
    developers, features, and stories for E2E testing.

    Args:
        e2e_app: The DIContainer fixture.

    Yields:
        SQLiteUnitOfWork with populated data.

    Test Data:
        - 5 developers (Dev 1-5)
        - 2 features (Feature 1 wave 1, Feature 2 wave 2)
        - 10 stories (TEST-001 to TEST-010, 5 per feature)
    """
    async with e2e_app.create_unit_of_work() as uow:
        # Create 5 developers
        for i in range(1, 6):
            dev = Developer(name=f"Dev {i}")
            await uow.developers.add(dev)

        # Create 2 features
        feature1 = Feature(name="Feature 1", wave=1)
        feature2 = Feature(name="Feature 2", wave=2)
        await uow.features.add(feature1)
        await uow.features.add(feature2)

        # Create 10 stories
        for i in range(1, 11):
            story = Story(
                id=f"TEST-{i:03d}",
                component="TEST",
                name=f"Historia {i}",
                story_points=StoryPoint(5),
                priority=i,
                status=StoryStatus.BACKLOG,
                feature_id=1 if i <= 5 else 2,
            )
            await uow.stories.add(story)

        await uow.commit()
        yield uow


# ============================================================================
# Helper Fixtures for Modal Dialog Handling (T026)
# ============================================================================


@pytest.fixture
def modal_handler():
    """Fixture factory for handling modal dialogs.

    Returns a function that schedules an action to run when a
    modal dialog is shown, using QTimer.singleShot.

    Returns:
        Function to schedule modal dialog handlers.

    Example:
        def test_delete_with_confirm(modal_handler, e2e_main_window):
            def accept_dialog():
                dialog = e2e_main_window.findChild(QMessageBox)
                if dialog:
                    dialog.accept()

            modal_handler(accept_dialog, delay=100)
            # Trigger action that opens dialog
            e2e_main_window._on_delete_story()
    """

    def _schedule_handler(handler, delay: int = 100):
        """Schedule a handler to run after delay milliseconds.

        Args:
            handler: Callable to execute when dialog appears.
            delay: Milliseconds to wait before executing handler.
        """
        QTimer.singleShot(delay, handler)

    return _schedule_handler


# ============================================================================
# Pytest Configuration
# ============================================================================


def pytest_configure(config):
    """Configure pytest markers for E2E tests."""
    config.addinivalue_line("markers", "e2e: End-to-end tests with GUI")
    config.addinivalue_line("markers", "perf: Performance tests")
    config.addinivalue_line("markers", "slow: Slow tests (> 10s)")


# ============================================================================
# Auto-Close Modal Dialog Fixtures (T027)
# ============================================================================


@pytest.fixture(autouse=True)
def patch_message_boxes(monkeypatch):
    """Patch QMessageBox static methods to be non-blocking.

    This fixture automatically patches all QMessageBox static methods
    to return immediately without showing a dialog, enabling automated
    E2E testing without manual interaction.

    The call_history list can be used to verify which messages were shown.

    Args:
        monkeypatch: pytest monkeypatch fixture.

    Yields:
        List of tuples (type, title, text) for each message box call.

    Example:
        def test_allocation_shows_message(patch_message_boxes, e2e_main_window):
            # ... execute allocation ...
            assert any(
                msg[0] == "information" and "Alocacao" in msg[1]
                for msg in patch_message_boxes
            )
    """
    from PySide6.QtWidgets import QMessageBox

    call_history = []

    def mock_information(parent, title, text, *args, **kwargs):
        call_history.append(("information", title, text))
        return QMessageBox.StandardButton.Ok

    def mock_warning(parent, title, text, *args, **kwargs):
        call_history.append(("warning", title, text))
        return QMessageBox.StandardButton.Ok

    def mock_question(parent, title, text, *args, **kwargs):
        call_history.append(("question", title, text))
        return QMessageBox.StandardButton.Yes

    def mock_critical(parent, title, text, *args, **kwargs):
        call_history.append(("critical", title, text))
        return QMessageBox.StandardButton.Ok

    monkeypatch.setattr(QMessageBox, "information", mock_information)
    monkeypatch.setattr(QMessageBox, "warning", mock_warning)
    monkeypatch.setattr(QMessageBox, "question", mock_question)
    monkeypatch.setattr(QMessageBox, "critical", mock_critical)

    yield call_history
