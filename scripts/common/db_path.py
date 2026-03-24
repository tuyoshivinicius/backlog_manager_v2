"""Centralized database path resolution for analysis scripts.

This module provides consistent database path handling across all
analysis scripts (seed, extract_metrics, check_deps, validate).
"""

import logging
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def get_analysis_db_path(custom_path: Path | None = None) -> Path:
    """Get database path for analysis scripts.

    Priority:
    1. Custom path if provided
    2. Environment variable BACKLOG_DB_PATH
    3. Default app data location

    Args:
        custom_path: Optional custom database path.

    Returns:
        Path to the database file.
    """
    if custom_path:
        return custom_path

    env_path = os.environ.get("BACKLOG_DB_PATH")
    if env_path:
        return Path(env_path)

    # Import from main app to ensure consistency
    from backlog_manager.infrastructure.database.sqlite_connection import (
        get_database_path,
    )

    return get_database_path()


def log_database_info(db_path: Path) -> None:
    """Log database file information.

    Displays path, existence status, size, and last modification time.

    Args:
        db_path: Path to the database file.
    """
    print(f"Database: {db_path}")
    if db_path.exists():
        stat = db_path.stat()
        size_kb = stat.st_size / 1024
        modified = datetime.fromtimestamp(stat.st_mtime)
        print(f"  Size: {size_kb:.1f} KB")
        print(f"  Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("  WARNING: File does not exist!")


def add_db_path_argument(parser) -> None:
    """Add --db-path argument to argument parser.

    Args:
        parser: argparse.ArgumentParser instance.
    """
    parser.add_argument(
        "--db-path",
        type=Path,
        default=None,
        metavar="PATH",
        help="Custom database path (default: app default)",
    )


def validate_db_path(db_path: Path | None) -> None:
    """Validate that db_path directory exists.

    Args:
        db_path: Database path to validate.

    Raises:
        ValueError: If directory does not exist.
    """
    if db_path is not None:
        parent = db_path.parent
        if not parent.exists():
            raise ValueError(
                f"Directory does not exist: {parent}. Create the directory first."
            )
