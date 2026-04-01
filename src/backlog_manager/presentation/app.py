"""Application entry point with qasync integration.

This module provides the main entry point for the Backlog Manager GUI application.
It integrates asyncio with Qt's event loop using qasync.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop

from backlog_manager.infrastructure.database.sqlite_connection import (
    get_database_path,
    init_database,
)
from backlog_manager.infrastructure.logging.logger_config import (
    get_logger,
    setup_logging,
)
from backlog_manager.presentation.container import DIContainer
from backlog_manager.presentation.theme import (
    DESIGN_TOKENS,
    _initialize_icon_manager,
    apply_theme,
)

if TYPE_CHECKING:
    pass  # Required for conditional imports used by type checkers only

# Configure logging to use %APPDATA%/BacklogManager/logs
setup_logging()
logger = get_logger(__name__)


def _load_and_apply_theme(app: QApplication) -> None:
    """Load and apply the design system theme to the application.

    Args:
        app: The QApplication instance to apply the theme to.

    This function loads the stylesheet.qss template, substitutes design tokens,
    and applies the resulting stylesheet to the application. If loading fails,
    it logs a warning and continues with default Qt styling.
    """
    try:
        qss_path = Path(__file__).parent / "theme" / "stylesheet.qss"
        if qss_path.exists():
            qss_template = qss_path.read_text(encoding="utf-8")
            stylesheet = apply_theme(qss_template, DESIGN_TOKENS)
            app.setStyleSheet(stylesheet)
            logger.debug("Design system theme applied successfully")
        else:
            logger.warning(
                "stylesheet.qss not found at %s, using default styling", qss_path
            )
    except Exception as e:
        logger.warning("Failed to load theme, using default styling: %s", e)


def get_default_db_path() -> Path:
    """Get the default database path from infrastructure layer.

    Returns:
        Path to the default database file.
    """
    return get_database_path()


async def run_application(db_path: Path | None = None) -> int:
    """Run the application asynchronously.

    Args:
        db_path: Optional path to the database file. If None, uses default.

    Returns:
        Exit code (0 for success).
    """
    from backlog_manager.presentation.views.main_window import MainWindow

    # Use provided path or default
    if db_path is None:
        db_path = get_default_db_path()

    logger.info("Starting Backlog Manager with database: %s", db_path)

    # Initialize database (creates tables if they don't exist)
    await init_database(db_path)

    # Initialize DI container
    container = DIContainer.initialize(db_path)

    # Create main window
    window = MainWindow(container.main_window_viewmodel)
    window.show()

    logger.info("Main window displayed")

    # Load initial data
    await container.main_window_viewmodel.load_stories()
    logger.info("Initial data loaded")

    # Keep the event loop running while the window is visible
    while window.isVisible():
        await asyncio.sleep(0.05)

    logger.info("Application shutting down")

    # Cancel all pending tasks to avoid RuntimeError on shutdown
    pending_tasks = [
        task
        for task in asyncio.all_tasks()
        if task is not asyncio.current_task() and not task.done()
    ]
    if pending_tasks:
        logger.debug("Cancelling %d pending tasks", len(pending_tasks))
        for task in pending_tasks:
            task.cancel()
        # Wait briefly for tasks to be cancelled
        await asyncio.gather(*pending_tasks, return_exceptions=True)

    return 0


def main(db_path: str | None = None) -> int:
    """Main entry point for the application.

    Args:
        db_path: Optional path to the database file as string.

    Returns:
        Exit code from the application.
    """
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create the Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Backlog Manager")
    app.setOrganizationName("BacklogManager")

    # Apply design system theme (T032, T033)
    _load_and_apply_theme(app)

    # Initialize icon manager for eager loading (T078.1)
    _initialize_icon_manager()
    logger.debug("Icon manager initialized")

    # Set up qasync event loop
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Parse database path
    path = Path(db_path) if db_path else None

    try:
        with loop:
            exit_code = loop.run_until_complete(run_application(path))
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        exit_code = 0
    except RuntimeError as e:
        # Handle qasync shutdown RuntimeError gracefully
        if "Event loop stopped before Future completed" in str(e):
            logger.debug(
                "Application closed with pending async operations (normal shutdown)"
            )
            exit_code = 0
        else:
            logger.exception("Runtime error")
            exit_code = 1
    except Exception:
        logger.exception("Application error")
        exit_code = 1
    finally:
        # Clean up container
        DIContainer.reset()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
