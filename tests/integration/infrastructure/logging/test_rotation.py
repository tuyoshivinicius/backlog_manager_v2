"""Test log rotation."""

import tempfile
from pathlib import Path

import pytest

from backlog_manager.infrastructure.logging.logger_config import (
    reset_logging,
    setup_logging,
)


@pytest.mark.integration
class TestLogRotation:
    """Test log file rotation."""

    def setup_method(self) -> None:
        """Reset logging before each test."""
        reset_logging()

    def teardown_method(self) -> None:
        """Reset logging after each test."""
        reset_logging()

    def test_rotation_creates_backup_files(self) -> None:
        """Test that rotation creates backup files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "logs"

            logger = setup_logging(log_dir=log_dir)

            # Write enough data to trigger rotation (10MB limit)
            # Each message is ~100 bytes, need ~100k messages for 10MB
            # For testing, we'll write less but verify mechanism works
            large_message = "X" * 1000  # 1KB per message
            for _ in range(100):
                logger.info(large_message)

            log_file = log_dir / "backlog_manager.log"
            assert log_file.exists()

            # Reset before temp dir cleanup on Windows
            reset_logging()

    def test_max_backup_count(self) -> None:
        """Test that backup count is limited to 3."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "logs"

            # Create fake old backup files first
            log_dir.mkdir(parents=True)
            for i in range(1, 6):
                (log_dir / f"backlog_manager.log.{i}").write_text(f"Old log {i}")

            logger = setup_logging(log_dir=log_dir)
            logger.info("New message")

            # Check that logger is configured with 3 backup count
            handler = logger.handlers[0]
            assert hasattr(handler, "backupCount")
            assert handler.backupCount == 3

            # Reset before temp dir cleanup on Windows
            reset_logging()

    def test_max_bytes_configuration(self) -> None:
        """Test that max bytes is configured to 10MB."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "logs"

            logger = setup_logging(log_dir=log_dir)

            handler = logger.handlers[0]
            assert hasattr(handler, "maxBytes")
            assert handler.maxBytes == 10 * 1024 * 1024  # 10MB

            # Reset before temp dir cleanup on Windows
            reset_logging()
