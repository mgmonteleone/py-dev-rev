"""Logging configuration for DevRev SDK.

This module provides structured logging with optional color support
for development environments.
"""

import logging
import sys
from typing import Literal

LogLevel = Literal["DEBUG", "INFO", "WARN", "WARNING", "ERROR"]


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
) -> None:
    """Configure SDK-wide logging.

    Args:
        level: Logging level
        use_colors: Whether to use colored output

    Example:
        ```python
        from devrev.utils.logging import configure_logging

        configure_logging(level="DEBUG", use_colors=True)
        ```
    """
    normalized_level = "WARNING" if level == "WARN" else level

    logger = logging.getLogger("devrev")
    logger.setLevel(getattr(logging, normalized_level))

    # Clear existing handlers
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColoredFormatter(use_colors=use_colors))
    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False
