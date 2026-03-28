"""Logging configuration for Backlog Manager."""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

_logger: logging.Logger | None = None


def get_log_directory() -> Path:
    """Get the log directory path.

    Returns:
        Path to the log directory.
    """
    app_data = Path(os.environ.get("APPDATA", Path.home()))
    log_dir = app_data / "BacklogManager" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logging(
    level: int = logging.INFO,
    log_dir: Path | None = None,
) -> logging.Logger:
    """Configure logging with file rotation.

    Sets up a logger with:
    - RotatingFileHandler with 10MB max size and 3 backups
    - ISO 8601 timestamp format
    - Level, name, and message in log format

    Args:
        level: Logging level (default: INFO).
        log_dir: Directory for log files (default: AppData/BacklogManager/logs).

    Returns:
        Configured logger instance.
    """
    global _logger

    if _logger is not None:
        return _logger

    if log_dir is None:
        log_dir = get_log_directory()
    else:
        # Ensure the provided directory exists
        log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "backlog_manager.log"

    handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=3,
        encoding="utf-8",
    )

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger("backlog_manager")
    logger.addHandler(handler)
    logger.setLevel(level)

    _logger = logger
    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (will be prefixed with 'backlog_manager.').
              If None, returns the root backlog_manager logger.

    Returns:
        Logger instance.
    """
    if name is None:
        return setup_logging()

    return logging.getLogger(f"backlog_manager.{name}")


def reset_logging() -> None:
    """Reset logging configuration.

    Useful for testing to ensure clean state.
    """
    global _logger

    if _logger is not None:
        for handler in _logger.handlers[:]:
            handler.flush()
            handler.close()
            _logger.removeHandler(handler)
        _logger = None

    # Also clear any handlers from the named logger
    named_logger = logging.getLogger("backlog_manager")
    for handler in named_logger.handlers[:]:
        handler.flush()
        handler.close()
        named_logger.removeHandler(handler)
