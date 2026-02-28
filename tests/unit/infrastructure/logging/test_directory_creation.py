"""Test logging directory creation."""

import tempfile
from pathlib import Path

import pytest

from backlog_manager.infrastructure.logging.logger_config import (
    reset_logging,
    setup_logging,
)


@pytest.mark.unit
class TestDirectoryCreation:
    """Test log directory creation."""

    def setup_method(self) -> None:
        """Reset logging before each test."""
        reset_logging()

    def teardown_method(self) -> None:
        """Reset logging after each test."""
        reset_logging()

    def test_creates_log_directory(self) -> None:
        """Test that setup_logging creates log directory if not exists."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "logs"
            assert not log_dir.exists()

            setup_logging(log_dir=log_dir)

            assert log_dir.exists()
            assert log_dir.is_dir()

            # Reset before temp dir cleanup on Windows
            reset_logging()

    def test_creates_nested_directory(self) -> None:
        """Test that setup_logging creates nested directories."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "deep" / "nested" / "logs"
            assert not log_dir.exists()

            setup_logging(log_dir=log_dir)

            assert log_dir.exists()
            assert log_dir.is_dir()

            # Reset before temp dir cleanup on Windows
            reset_logging()

    def test_existing_directory_no_error(self) -> None:
        """Test that existing directory doesn't cause error."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "logs"
            log_dir.mkdir(parents=True)

            # Should not raise
            setup_logging(log_dir=log_dir)

            assert log_dir.exists()

            # Reset before temp dir cleanup on Windows
            reset_logging()

    def test_creates_log_file(self) -> None:
        """Test that setup_logging creates log file."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "logs"

            logger = setup_logging(log_dir=log_dir)
            logger.info("Test message")

            log_file = log_dir / "backlog_manager.log"
            assert log_file.exists()

            # Reset before temp dir cleanup on Windows
            reset_logging()
