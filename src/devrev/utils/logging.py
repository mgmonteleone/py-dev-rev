"""Logging configuration for DevRev SDK.

This module provides structured logging with optional color support
for development environments and JSON formatting for production.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    pass

LogLevel = Literal["DEBUG", "INFO", "WARN", "WARNING", "ERROR"]
LogFormat = Literal["text", "json"]


class JSONFormatter(logging.Formatter):
    """Formatter that outputs logs as JSON for production environments.

    Produces structured JSON logs compatible with cloud logging services
    like Google Cloud Logging, AWS CloudWatch, and ELK stack.

    Attributes:
        service_name: Name of the service for log correlation
        include_timestamp: Whether to include ISO timestamp
    """

    def __init__(
        self,
        service_name: str = "devrev-sdk",
        include_timestamp: bool = True,
        extra_fields: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the JSON formatter.

        Args:
            service_name: Name of the service for log correlation
            include_timestamp: Whether to include ISO timestamp
            extra_fields: Additional fields to include in every log entry
        """
        super().__init__()
        self.service_name = service_name
        self.include_timestamp = include_timestamp
        self.extra_fields = extra_fields or {}

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log string
        """
        log_data: dict[str, Any] = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "service": self.service_name,
        }

        if self.include_timestamp:
            log_data["timestamp"] = datetime.now(UTC).isoformat()

        # Add extra fields
        log_data.update(self.extra_fields)

        # Add location info only for DEBUG level to minimize log volume
        # and avoid exposing file path details in production logs
        if record.levelno == logging.DEBUG:
            log_data["source"] = {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName,
            }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Include any extra attributes from the record
        # Filter out standard LogRecord attributes
        standard_attrs = {
            "name",
            "msg",
            "args",
            "created",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "exc_info",
            "exc_text",
            "thread",
            "threadName",
            "taskName",
            "message",
        }
        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith("_"):
                log_data[key] = value

        return json.dumps(log_data, default=str)


class ColoredFormatter(logging.Formatter):
    """Formatter that adds colors to log output.

    Colors are only applied when outputting to a TTY terminal.
    Falls back to plain text when colors aren't supported.
    """

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "WARN": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        use_colors: bool = True,
    ) -> None:
        """Initialize the colored formatter.

        Args:
            fmt: Log message format string
            datefmt: Date format string
            use_colors: Whether to use colors (auto-detected if True)
        """
        super().__init__(fmt or self._default_format(), datefmt or "%Y-%m-%d %H:%M:%S")
        self.use_colors = use_colors and self._supports_color()

    @staticmethod
    def _default_format() -> str:
        """Get the default log format string."""
        return "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    @staticmethod
    def _supports_color() -> bool:
        """Check if terminal supports colors."""
        if not hasattr(sys.stdout, "isatty"):
            return False
        return sys.stdout.isatty()

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with optional color."""
        if self.use_colors:
            color = self.COLORS.get(record.levelname, "")
            # Store original levelname
            original_levelname = record.levelname
            record.levelname = f"{color}{record.levelname}{self.RESET}"
            result = super().format(record)
            # Restore original levelname
            record.levelname = original_levelname
            return result
        return super().format(record)


def get_logger(
    name: str = "devrev",
    level: LogLevel = "WARN",
) -> logging.Logger:
    """Get a configured logger instance.

    Args:
        name: Logger name (default: "devrev")
        level: Logging level (default: "WARN")

    Returns:
        Configured logger instance

    Example:
        ```python
        from devrev.utils.logging import get_logger

        logger = get_logger("devrev.http", level="DEBUG")
        logger.debug("Making request to /accounts.list")
        ```
    """
    logger = logging.getLogger(name)

    # Normalize level
    normalized_level = "WARNING" if level == "WARN" else level
    logger.setLevel(getattr(logging, normalized_level))

    # Only add handler if logger doesn't have one
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(ColoredFormatter())
        logger.addHandler(handler)

    return logger


def configure_logging(
    level: LogLevel = "WARN",
    use_colors: bool = True,
    log_format: LogFormat = "text",
    service_name: str = "devrev-sdk",
    extra_fields: dict[str, Any] | None = None,
) -> None:
    """Configure SDK-wide logging.

    Args:
        level: Logging level
        use_colors: Whether to use colored output (only for text format)
        log_format: Output format - "text" for human-readable, "json" for structured
        service_name: Service name for JSON logs (useful for log correlation)
        extra_fields: Additional fields to include in every JSON log entry

    Example:
        ```python
        from devrev.utils.logging import configure_logging

        # Development mode with colors
        configure_logging(level="DEBUG", use_colors=True)

        # Production mode with JSON logging
        configure_logging(
            level="INFO",
            log_format="json",
            service_name="my-app",
            extra_fields={"environment": "production"},
        )
        ```
    """
    normalized_level = "WARNING" if level == "WARN" else level

    logger = logging.getLogger("devrev")
    logger.setLevel(getattr(logging, normalized_level))

    # Clear existing handlers
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if log_format == "json":
        handler.setFormatter(
            JSONFormatter(
                service_name=service_name,
                extra_fields=extra_fields,
            )
        )
    else:
        handler.setFormatter(ColoredFormatter(use_colors=use_colors))

    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False
