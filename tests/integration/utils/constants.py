"""Constants for integration test utilities.

Defines naming conventions, resource types, and configuration
for write operation integration tests.
"""

from typing import Final

# Prefix for all test data - enables identification and cleanup
TEST_PREFIX: Final[str] = "SDK_TEST_"

# Maximum length for generated names (API constraints)
MAX_NAME_LENGTH: Final[int] = 100

# Resource types supported by TestDataManager
RESOURCE_TYPES: Final[frozenset[str]] = frozenset(
    {
        "account",
        "article",
        "conversation",
        "group",
        "link",
        "part",
        "question_answer",
        "rev_user",
        "tag",
        "webhook",
        "work",
    }
)

# Resource deletion order (respects dependencies)
# Resources are deleted in reverse order of this list
DELETION_ORDER: Final[tuple[str, ...]] = (
    "link",  # Delete links first (references other resources)
    "work",  # Then work items
    "article",  # Then articles
    "question_answer",  # Then question answers
    "webhook",  # Then webhooks
    "tag",  # Then tags
    "group",  # Then groups
    "part",  # Then parts
    "conversation",  # Then conversations
    "rev_user",  # Then rev users
    "account",  # Delete accounts last (may have dependencies)
)

# Environment variable names
ENV_WRITE_TESTS_ENABLED: Final[str] = "DEVREV_WRITE_TESTS_ENABLED"
ENV_TEST_API_TOKEN: Final[str] = "DEVREV_TEST_API_TOKEN"
ENV_BASE_URL: Final[str] = "DEVREV_BASE_URL"

# Rate limiting defaults
DEFAULT_REQUESTS_PER_SECOND: Final[float] = 2.0
DEFAULT_MIN_INTERVAL_SECONDS: Final[float] = 0.5
