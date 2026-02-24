"""Test data manager for write operation integration tests.

Provides lifecycle management for test data including:
- Unique naming with test prefix and run isolation
- Resource tracking for automatic cleanup
- Rate limiting to protect APIs
- Cleanup with dependency ordering
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import TYPE_CHECKING

from tests.integration.utils.cleanup import CleanupReport
from tests.integration.utils.constants import (
    DEFAULT_MIN_INTERVAL_SECONDS,
    DELETION_ORDER,
    MAX_NAME_LENGTH,
    RESOURCE_TYPES,
    TEST_PREFIX,
)

if TYPE_CHECKING:
    from devrev.client import DevRevClient

logger = logging.getLogger(__name__)


class TestDataManager:
    """Manages test data lifecycle with automatic cleanup.

    This class provides:
    - Unique naming for test resources using SDK_TEST_ prefix
    - Run isolation via unique run IDs
    - Resource tracking for automatic cleanup
    - Rate limiting to prevent API throttling
    - Dependency-aware cleanup ordering

    Example:
        >>> manager = TestDataManager(client)
        >>> name = manager.generate_name("MyAccount")
        >>> account = client.accounts.create(display_name=name)
        >>> manager.register("account", account.id)
        >>> # ... run tests ...
        >>> report = manager.cleanup()  # Deletes all registered resources
    """

    def __init__(
        self,
        client: DevRevClient,
        *,
        run_id: str | None = None,
        rate_limit: float = DEFAULT_MIN_INTERVAL_SECONDS,
    ) -> None:
        """Initialize the test data manager.

        Args:
            client: DevRev client for API operations.
            run_id: Optional run ID for isolation. Auto-generated if not provided.
            rate_limit: Minimum seconds between API calls.
        """
        self._client = client
        self._run_id = run_id or uuid.uuid4().hex[:8]
        self._rate_limit = rate_limit
        self._last_request_time: float = 0.0
        self._created_resources: list[tuple[str, str]] = []

        logger.info(f"TestDataManager initialized with run_id: {self._run_id}")

    @property
    def run_id(self) -> str:
        """Unique identifier for this test run."""
        return self._run_id

    @property
    def client(self) -> DevRevClient:
        """DevRev client instance."""
        return self._client

    def generate_name(self, base_name: str) -> str:
        """Generate a unique test name with proper prefix.

        Creates a name that:
        - Starts with SDK_TEST_ for easy identification
        - Includes run_id for isolation between concurrent runs
        - Truncates if necessary to respect API limits

        Args:
            base_name: Base name for the resource.

        Returns:
            Formatted test name like "SDK_TEST_a1b2c3d4_MyResource".
        """
        full_name = f"{TEST_PREFIX}{self._run_id}_{base_name}"

        if len(full_name) > MAX_NAME_LENGTH:
            # Truncate base_name while keeping prefix and run_id
            prefix_len = len(TEST_PREFIX) + len(self._run_id) + 1
            max_base = MAX_NAME_LENGTH - prefix_len
            full_name = f"{TEST_PREFIX}{self._run_id}_{base_name[:max_base]}"

        return full_name

    def register(self, resource_type: str, resource_id: str) -> None:
        """Register a created resource for cleanup.

        Args:
            resource_type: Type of resource (e.g., "account", "tag").
            resource_id: Unique identifier of the resource.

        Raises:
            ValueError: If resource_type is not supported.
        """
        if resource_type not in RESOURCE_TYPES:
            raise ValueError(
                f"Unknown resource type: {resource_type}. Supported types: {sorted(RESOURCE_TYPES)}"
            )

        self._created_resources.append((resource_type, resource_id))
        logger.debug(f"Registered {resource_type}/{resource_id} for cleanup")

    def _throttle(self) -> None:
        """Ensure minimum interval between API requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._rate_limit:
            time.sleep(self._rate_limit - elapsed)
        self._last_request_time = time.time()

    def _get_deletion_priority(self, resource_type: str) -> int:
        """Get deletion priority for a resource type.

        Lower numbers are deleted first.
        """
        try:
            return DELETION_ORDER.index(resource_type)
        except ValueError:
            return len(DELETION_ORDER)  # Unknown types deleted last

    def _sort_for_deletion(
        self,
        resources: list[tuple[str, str]],
    ) -> list[tuple[str, str]]:
        """Sort resources for deletion respecting dependencies."""
        return sorted(resources, key=lambda r: self._get_deletion_priority(r[0]))

    def _delete_resource(self, resource_type: str, resource_id: str) -> bool:
        """Delete a single resource by type and ID.

        Args:
            resource_type: Type of resource to delete.
            resource_id: ID of the resource to delete.

        Returns:
            True if deletion was attempted, False if no delete method exists.

        Raises:
            Exception: If deletion fails.
        """
        self._throttle()

        # Note: Only include resource types that have delete() methods in the SDK.
        # Unsupported types: group (no delete), conversation (no delete),
        # part (no delete), rev_user (no delete)
        delete_methods = {
            "account": lambda rid: self._client.accounts.delete(rid),
            "tag": lambda rid: self._client.tags.delete(
                __import__("devrev.models.tags", fromlist=["TagsDeleteRequest"]).TagsDeleteRequest(
                    id=rid
                )
            ),
            "work": lambda rid: self._client.works.delete(rid),
            "article": lambda rid: self._client.articles.delete(
                __import__(
                    "devrev.models.articles", fromlist=["ArticlesDeleteRequest"]
                ).ArticlesDeleteRequest(id=rid)
            ),
            "question_answer": lambda rid: self._client.question_answers.delete(
                __import__(
                    "devrev.models.question_answers", fromlist=["QuestionAnswersDeleteRequest"]
                ).QuestionAnswersDeleteRequest(id=rid)
            ),
            "webhook": lambda rid: self._client.webhooks.delete(
                __import__(
                    "devrev.models.webhooks", fromlist=["WebhooksDeleteRequest"]
                ).WebhooksDeleteRequest(id=rid)
            ),
            "link": lambda rid: self._client.links.delete(
                __import__(
                    "devrev.models.links", fromlist=["LinksDeleteRequest"]
                ).LinksDeleteRequest(id=rid)
            ),
        }

        if resource_type in delete_methods:
            delete_methods[resource_type](resource_id)
            return True
        else:
            # Return False to indicate cleanup was not possible - caller should track this
            logger.warning(
                f"No delete method for resource type: {resource_type}. "
                f"Resource {resource_id} may be orphaned."
            )
            return False

    def cleanup(self) -> CleanupReport:
        """Delete all registered resources in dependency order.

        Resources are deleted in an order that respects dependencies
        (e.g., links before the resources they reference).

        Returns:
            CleanupReport with success/failure details for each resource.
        """
        report = CleanupReport(run_id=self._run_id)

        if not self._created_resources:
            logger.info("No resources to cleanup")
            return report

        sorted_resources = self._sort_for_deletion(self._created_resources)
        logger.info(f"Cleaning up {len(sorted_resources)} resources...")

        for resource_type, resource_id in sorted_resources:
            try:
                deleted = self._delete_resource(resource_type, resource_id)
                if deleted:
                    report.add_success(resource_type, resource_id)
                else:
                    report.add_skipped(
                        resource_type,
                        resource_id,
                        f"No delete method available for {resource_type}",
                    )
            except Exception as e:
                report.add_failure(resource_type, resource_id, str(e))

        # Clear the tracking list
        self._created_resources.clear()

        report.log_summary()
        return report

    def get_registered_count(self) -> int:
        """Get count of registered resources pending cleanup."""
        return len(self._created_resources)

    def is_test_resource(self, name: str) -> bool:
        """Check if a resource name matches our test naming convention.

        Args:
            name: Resource name to check.

        Returns:
            True if name starts with SDK_TEST_ prefix.
        """
        return name.startswith(TEST_PREFIX)

    def is_our_run(self, name: str) -> bool:
        """Check if a resource belongs to this test run.

        Args:
            name: Resource name to check.

        Returns:
            True if name matches this run's prefix pattern.
        """
        return name.startswith(f"{TEST_PREFIX}{self._run_id}_")
