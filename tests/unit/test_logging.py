"""Unit tests for logging infrastructure."""

import json
import logging

from devrev.utils.logging import ColoredFormatter, JSONFormatter, configure_logging, get_logger


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


class TestJSONFormatter:
    """Tests for JSONFormatter class."""

    def test_basic_json_format(self) -> None:
        """Test basic JSON formatting."""
        formatter = JSONFormatter(service_name="test-service")
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        assert log_data["severity"] == "INFO"
        assert log_data["message"] == "Test message"
        assert log_data["logger"] == "test.logger"
        assert log_data["service"] == "test-service"
        assert "timestamp" in log_data

    def test_json_format_without_timestamp(self) -> None:
        """Test JSON formatting without timestamp."""
        formatter = JSONFormatter(include_timestamp=False)
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg="Warning message",
            args=(),
            exc_info=None,
        )
        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        assert "timestamp" not in log_data
        assert log_data["severity"] == "WARNING"

    def test_json_format_with_extra_fields(self) -> None:
        """Test JSON formatting with extra fields."""
        extra = {"environment": "production", "version": "1.0.0"}
        formatter = JSONFormatter(extra_fields=extra)
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
        log_data = json.loads(formatted)

        assert log_data["environment"] == "production"
        assert log_data["version"] == "1.0.0"

    def test_json_format_debug_includes_source(self) -> None:
        """Test that DEBUG level includes source location."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="/path/to/test.py",
            lineno=123,
            msg="Debug message",
            args=(),
            exc_info=None,
        )
        record.funcName = "test_function"
        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        assert "source" in log_data
        assert log_data["source"]["file"] == "test.py"
        assert log_data["source"]["line"] == 123
        assert log_data["source"]["function"] == "test_function"

    def test_json_format_info_excludes_source(self) -> None:
        """Test that INFO level excludes source location."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="/path/to/test.py",
            lineno=123,
            msg="Info message",
            args=(),
            exc_info=None,
        )
        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        assert "source" not in log_data

    def test_json_format_with_exception(self) -> None:
        """Test JSON formatting with exception info."""
        formatter = JSONFormatter()
        try:
            raise ValueError("Test error")
        except ValueError:
            import sys

            exc_info = sys.exc_info()
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=1,
                msg="Error with exception",
                args=(),
                exc_info=exc_info,
            )
            formatted = formatter.format(record)
            log_data = json.loads(formatted)

            assert "exception" in log_data
            assert "ValueError: Test error" in log_data["exception"]
            assert "Traceback" in log_data["exception"]

    def test_json_format_with_custom_attributes(self) -> None:
        """Test JSON formatting includes custom record attributes."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Message with custom attrs",
            args=(),
            exc_info=None,
        )
        # Add custom attributes
        record.request_id = "req-123"
        record.user_id = "user-456"

        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        assert log_data["request_id"] == "req-123"
        assert log_data["user_id"] == "user-456"

    def test_json_format_excludes_private_attributes(self) -> None:
        """Test that private attributes (starting with _) are excluded."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record._private_attr = "should not appear"
        record.public_attr = "should appear"

        formatted = formatter.format(record)
        log_data = json.loads(formatted)

        assert "_private_attr" not in log_data
        assert log_data["public_attr"] == "should appear"
