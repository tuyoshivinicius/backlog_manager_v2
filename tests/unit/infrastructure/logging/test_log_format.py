"""Test log format."""

import re
import tempfile
from pathlib import Path

import pytest
from backlog_manager.infrastructure.logging.logger_config import (
    reset_logging,
    setup_logging,
)


@pytest.mark.unit
class TestLogFormat:
    """Test log format configuration."""

    def setup_method(self) -> None:
        """Reset logging before each test."""
        reset_logging()

    def teardown_method(self) -> None:
        """Reset logging after each test."""
        reset_logging()

    def test_iso8601_timestamp_format(self) -> None:
        """Test that log entries use ISO 8601 timestamp format."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "logs"

            logger = setup_logging(log_dir=log_dir)
            logger.info("Test message")

            # Reset to release file handle before reading
            reset_logging()

            log_file = log_dir / "backlog_manager.log"
            content = log_file.read_text(encoding="utf-8")

            # ISO 8601 format: YYYY-MM-DDTHH:MM:SS
            iso_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
            assert re.search(iso_pattern, content) is not None

    def test_log_contains_level(self) -> None:
        """Test that log entries contain log level."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "logs"

            logger = setup_logging(log_dir=log_dir)
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")

            # Reset to release file handle before reading
            reset_logging()

            log_file = log_dir / "backlog_manager.log"
            content = log_file.read_text(encoding="utf-8")

            assert "INFO" in content
            assert "WARNING" in content
            assert "ERROR" in content

    def test_log_contains_logger_name(self) -> None:
        """Test that log entries contain logger name."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "logs"

            logger = setup_logging(log_dir=log_dir)
            logger.info("Test message")

            # Reset to release file handle before reading
            reset_logging()

            log_file = log_dir / "backlog_manager.log"
            content = log_file.read_text(encoding="utf-8")

            assert "backlog_manager" in content

    def test_log_contains_message(self) -> None:
        """Test that log entries contain the message."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "logs"

            logger = setup_logging(log_dir=log_dir)
            test_message = "This is a unique test message 12345"
            logger.info(test_message)

            # Reset to release file handle before reading
            reset_logging()

            log_file = log_dir / "backlog_manager.log"
            content = log_file.read_text(encoding="utf-8")

            assert test_message in content

    def test_log_format_structure(self) -> None:
        """Test complete log format structure."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "logs"

            logger = setup_logging(log_dir=log_dir)
            logger.info("Test message")

            # Reset to release file handle before reading
            reset_logging()

            log_file = log_dir / "backlog_manager.log"
            content = log_file.read_text(encoding="utf-8").strip()

            # Format: TIMESTAMP - LEVEL - NAME - MESSAGE
            parts = content.split(" - ")
            assert len(parts) >= 4

            # Timestamp
            assert re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", parts[0])
            # Level
            assert parts[1] == "INFO"
            # Name
            assert "backlog_manager" in parts[2]
            # Message
            assert "Test message" in " - ".join(parts[3:])

    def test_utf8_encoding(self) -> None:
        """Test that log file uses UTF-8 encoding."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "logs"

            logger = setup_logging(log_dir=log_dir)
            logger.info("Mensagem com acentuacao: e, a, o, u, c")

            # Reset to release file handle before reading
            reset_logging()

            log_file = log_dir / "backlog_manager.log"
            content = log_file.read_text(encoding="utf-8")

            assert "acentuacao" in content
