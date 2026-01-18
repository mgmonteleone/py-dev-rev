"""Cleanup utilities and reporting for test data management.

Provides data structures for tracking cleanup operations
and reporting on success/failure of resource deletion.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger(__name__)


@dataclass
class CleanupResult:
    """Result of a single cleanup operation."""

    resource_type: str
    resource_id: str
    success: bool
    error: str | None = None

    def __str__(self) -> str:
        if self.success:
            return f"✓ {self.resource_type}/{self.resource_id}"
        return f"✗ {self.resource_type}/{self.resource_id}: {self.error}"


@dataclass
class CleanupReport:
    """Comprehensive report of cleanup operation results.

    Tracks successes and failures during test data cleanup,
    providing detailed reporting for debugging and auditing.

    Attributes:
        results: List of individual cleanup results.
        run_id: Unique identifier for the test run.
    """

    results: list[CleanupResult] = field(default_factory=list)
    run_id: str = ""

    def add_success(self, resource_type: str, resource_id: str) -> None:
        """Record a successful cleanup.

        Args:
            resource_type: Type of resource (e.g., "account", "tag").
            resource_id: Unique identifier of the deleted resource.
        """
        self.results.append(
            CleanupResult(
                resource_type=resource_type,
                resource_id=resource_id,
                success=True,
            )
        )
        logger.debug(f"Cleaned up {resource_type}/{resource_id}")

    def add_failure(
        self,
        resource_type: str,
        resource_id: str,
        error: str,
    ) -> None:
        """Record a failed cleanup attempt.

        Args:
            resource_type: Type of resource (e.g., "account", "tag").
            resource_id: Unique identifier of the resource.
            error: Error message describing the failure.
        """
        self.results.append(
            CleanupResult(
                resource_type=resource_type,
                resource_id=resource_id,
                success=False,
                error=error,
            )
        )
        logger.warning(f"Failed to cleanup {resource_type}/{resource_id}: {error}")

    @property
    def successes(self) -> Sequence[CleanupResult]:
        """Get all successful cleanup results."""
        return [r for r in self.results if r.success]

    @property
    def failures(self) -> Sequence[CleanupResult]:
        """Get all failed cleanup results."""
        return [r for r in self.results if not r.success]

    @property
    def success_count(self) -> int:
        """Count of successful cleanups."""
        return len(self.successes)

    @property
    def failure_count(self) -> int:
        """Count of failed cleanups."""
        return len(self.failures)

    @property
    def all_succeeded(self) -> bool:
        """Check if all cleanup operations succeeded."""
        return self.failure_count == 0

    def __str__(self) -> str:
        """Generate human-readable cleanup report."""
        lines = [
            f"Cleanup Report (run_id: {self.run_id})",
            f"  Total: {len(self.results)}",
            f"  Successes: {self.success_count}",
            f"  Failures: {self.failure_count}",
        ]

        if self.failures:
            lines.append("  Failed resources:")
            for result in self.failures:
                lines.append(f"    - {result}")

        return "\n".join(lines)

    def log_summary(self) -> None:
        """Log cleanup summary at appropriate levels."""
        if self.all_succeeded:
            logger.info(f"Cleanup complete: {self.success_count} resources deleted")
        else:
            logger.error(
                f"Cleanup incomplete: {self.failure_count}/{len(self.results)} "
                f"resources failed to delete"
            )
            for result in self.failures:
                logger.error(f"  - {result}")
