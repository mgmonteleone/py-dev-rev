"""Unit tests for logging infrastructure."""

import logging

from devrev.utils.logging import ColoredFormatter, configure_logging, get_logger


class TestColoredFormatter:
    """Tests for ColoredFormatter class."""

    def test_default_format(self) -> None:
        """Test default format string."""
        formatter = ColoredFormatter(use_colors=False)
        assert "%(asctime)s" in formatter._fmt if formatter._fmt else False
        assert "%(levelname)s" in formatter._fmt if formatter._fmt else False
        assert "%(name)s" in formatter._fmt if formatter._fmt else False

    def test_format_without_colors(self) -> None:
        """Test formatting without colors."""
        formatter = ColoredFormatter(use_colors=False)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        formatted = formatter.format(record)
        assert "Test message" in formatted
        assert "\033[" not in formatted  # No ANSI codes

    def test_custom_format(self) -> None:
        """Test custom format string."""
        custom_fmt = "%(levelname)s - %(message)s"
        formatter = ColoredFormatter(fmt=custom_fmt, use_colors=False)
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Error occurred",
            args=(),
            exc_info=None,
        )
        formatted = formatter.format(record)
        assert "ERROR - Error occurred" in formatted


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_default(self) -> None:
        """Test getting default logger."""
        logger = get_logger()
        assert logger.name == "devrev"
        assert logger.level == logging.WARNING  # WARN normalized to WARNING

    def test_get_logger_custom_name(self) -> None:
        """Test getting logger with custom name."""
        logger = get_logger("devrev.http")
        assert logger.name == "devrev.http"

    def test_get_logger_debug_level(self) -> None:
        """Test getting logger with DEBUG level."""
        logger = get_logger("devrev.test", level="DEBUG")
        assert logger.level == logging.DEBUG

    def test_get_logger_warn_normalization(self) -> None:
        """Test that WARN is normalized to WARNING."""
        logger = get_logger("devrev.warn_test", level="WARN")
        assert logger.level == logging.WARNING


class TestConfigureLogging:
    """Tests for configure_logging function."""

    def test_configure_logging_default(self) -> None:
        """Test default logging configuration."""
        configure_logging()
        logger = logging.getLogger("devrev")
        assert logger.level == logging.WARNING

    def test_configure_logging_debug(self) -> None:
        """Test DEBUG level configuration."""
        configure_logging(level="DEBUG")
        logger = logging.getLogger("devrev")
        assert logger.level == logging.DEBUG

    def test_configure_logging_no_colors(self) -> None:
        """Test configuration without colors."""
        configure_logging(use_colors=False)
        logger = logging.getLogger("devrev")
        assert logger.handlers
        handler = logger.handlers[0]
        formatter = handler.formatter
        assert isinstance(formatter, ColoredFormatter)
        assert not formatter.use_colors

    def test_configure_logging_clears_existing_handlers(self) -> None:
        """Test that configure_logging clears existing handlers."""
        logger = logging.getLogger("devrev")
        # Add a dummy handler
        logger.addHandler(logging.StreamHandler())
        assert len(logger.handlers) >= 1  # Verify handler was added

        configure_logging()

        # Should have exactly one handler now
        assert len(logger.handlers) == 1
