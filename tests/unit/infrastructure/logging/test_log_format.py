"""Test log format."""

import logging
import re
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from backlog_manager.infrastructure.logging.logger_config import (
    get_log_directory,
    get_logger,
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

    def test_get_log_directory_returns_path(self) -> None:
        """Test that get_log_directory creates and returns a valid log path."""
        with (
            tempfile.TemporaryDirectory() as tmp_dir,
            patch.dict("os.environ", {"APPDATA": tmp_dir}),
        ):
            log_dir = get_log_directory()

            expected = Path(tmp_dir) / "BacklogManager" / "logs"
            assert log_dir == expected
            assert log_dir.exists()

    def test_get_log_directory_without_appdata(self) -> None:
        """Test get_log_directory falls back to home when APPDATA is unset."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            home_path = Path(tmp_dir) / "fakehome"
            home_path.mkdir()
            env_without_appdata = {
                k: v for k, v in __import__("os").environ.items() if k != "APPDATA"
            }
            with (
                patch.dict("os.environ", env_without_appdata, clear=True),
                patch.object(Path, "home", return_value=home_path),
            ):
                log_dir = get_log_directory()

                assert log_dir == home_path / "BacklogManager" / "logs"

    def test_setup_logging_returns_cached_logger(self) -> None:
        """Test that setup_logging returns cached logger on second call."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "logs"

            logger1 = setup_logging(log_dir=log_dir)
            logger2 = setup_logging(log_dir=log_dir)

            assert logger1 is logger2

            # Must reset before exiting context to release file handles
            reset_logging()

    def test_setup_logging_default_log_dir(self) -> None:
        """Test setup_logging uses get_log_directory when log_dir is None."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            with patch(
                "backlog_manager.infrastructure.logging.logger_config.get_log_directory",
                return_value=log_dir,
            ):
                logger = setup_logging(log_dir=None)

                assert logger is not None
                assert logger.name == "backlog_manager"

                # Must reset before exiting context to release file handles
                reset_logging()

    def test_get_logger_without_name_calls_setup(self) -> None:
        """Test get_logger with name=None returns root backlog_manager logger."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "logs"
            setup_logging(log_dir=log_dir)

            logger = get_logger(name=None)

            assert logger.name == "backlog_manager"

            # Must reset before exiting context to release file handles
            reset_logging()

    def test_get_logger_with_name_returns_child(self) -> None:
        """Test get_logger with a name returns a child logger."""
        logger = get_logger(name="test_module")

        assert logger.name == "backlog_manager.test_module"

    def test_reset_logging_cleans_named_logger_handlers(self) -> None:
        """Test reset_logging removes handlers from named logger even when _logger is None."""
        import backlog_manager.infrastructure.logging.logger_config as lc

        # Ensure _logger is None
        lc._logger = None

        # Add a handler directly to the named logger
        named_logger = logging.getLogger("backlog_manager")
        handler = logging.StreamHandler()
        named_logger.addHandler(handler)

        assert len(named_logger.handlers) > 0

        reset_logging()

        assert len(named_logger.handlers) == 0
