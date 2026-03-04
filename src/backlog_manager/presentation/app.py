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

from backlog_manager.infrastructure.database.sqlite_connection import init_database
from backlog_manager.infrastructure.logging.logger_config import (
    get_logger,
    setup_logging,
)
from backlog_manager.presentation.container import DIContainer

if TYPE_CHECKING:
    from backlog_manager.presentation.views.main_window import MainWindow

# Configure logging to use %APPDATA%/BacklogManager/logs
setup_logging()
logger = get_logger(__name__)

# Default database filename
DEFAULT_DB_NAME = "backlog_manager.db"


def get_default_db_path() -> Path:
    """Get the default database path in the current working directory.

    Returns:
        Path to the default database file.
    """
    return Path.cwd() / DEFAULT_DB_NAME


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
