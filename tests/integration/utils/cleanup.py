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
    skipped: bool = False  # True if cleanup was not possible (no delete method)

    def __str__(self) -> str:
        if self.skipped:
            return f"⚠ {self.resource_type}/{self.resource_id}: {self.error}"
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

    def add_skipped(
        self,
        resource_type: str,
        resource_id: str,
        reason: str,
    ) -> None:
        """Record a skipped cleanup (no delete method available).

        Args:
            resource_type: Type of resource (e.g., "group", "conversation").
            resource_id: Unique identifier of the resource.
            reason: Reason why cleanup was skipped.
        """
        self.results.append(
            CleanupResult(
                resource_type=resource_type,
                resource_id=resource_id,
                success=False,
                error=reason,
                skipped=True,
            )
        )
        logger.warning(
            f"Skipped cleanup for {resource_type}/{resource_id}: {reason} "
            f"(resource may be orphaned)"
        )

    @property
    def successes(self) -> Sequence[CleanupResult]:
        """Get all successful cleanup results."""
        return [r for r in self.results if r.success and not r.skipped]

    @property
    def failures(self) -> Sequence[CleanupResult]:
        """Get all failed cleanup results (excludes skipped)."""
        return [r for r in self.results if not r.success and not r.skipped]

    @property
    def skipped(self) -> Sequence[CleanupResult]:
        """Get all skipped cleanup results."""
        return [r for r in self.results if r.skipped]

    @property
    def success_count(self) -> int:
        """Count of successful cleanups."""
        return len(self.successes)

    @property
    def failure_count(self) -> int:
        """Count of failed cleanups."""
        return len(self.failures)

    @property
    def skipped_count(self) -> int:
        """Count of skipped cleanups (no delete method available)."""
        return len(self.skipped)

    @property
    def all_succeeded(self) -> bool:
        """Check if all cleanup operations succeeded (skipped counts as success)."""
        return self.failure_count == 0

    @property
    def has_orphaned_resources(self) -> bool:
        """Check if any resources may be orphaned (skipped or failed)."""
        return self.failure_count > 0 or self.skipped_count > 0

    def __str__(self) -> str:
        """Generate human-readable cleanup report."""
        lines = [
            f"Cleanup Report (run_id: {self.run_id})",
            f"  Total: {len(self.results)}",
            f"  Successes: {self.success_count}",
            f"  Failures: {self.failure_count}",
            f"  Skipped: {self.skipped_count}",
        ]

        if self.failures:
            lines.append("  Failed resources:")
            for result in self.failures:
                lines.append(f"    - {result}")

        if self.skipped:
            lines.append("  Skipped resources (may be orphaned):")
            for result in self.skipped:
                lines.append(f"    - {result}")

        return "\n".join(lines)

    def log_summary(self) -> None:
        """Log cleanup summary at appropriate levels."""
        if self.all_succeeded and self.skipped_count == 0:
            logger.info(f"Cleanup complete: {self.success_count} resources deleted")
        elif self.all_succeeded and self.skipped_count > 0:
            logger.warning(
                f"Cleanup complete with orphans: {self.success_count} deleted, "
                f"{self.skipped_count} skipped (no delete method)"
            )
            for result in self.skipped:
                logger.warning(f"  - {result}")
        else:
            logger.error(
                f"Cleanup incomplete: {self.failure_count} failed, "
                f"{self.skipped_count} skipped out of {len(self.results)} resources"
            )
            for result in self.failures:
                logger.error(f"  - {result}")
            for result in self.skipped:
                logger.warning(f"  - {result}")
