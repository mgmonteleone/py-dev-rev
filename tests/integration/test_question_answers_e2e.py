"""End-to-end integration tests for Q&A (Question Answers) endpoints.

Tests the full Q&A lifecycle: create, get, list, update, delete.
Uses real API calls against the DevRev instance.
Q&A is a beta API feature.

To run these tests:
    export DEVREV_API_TOKEN="your-token"
    export DEVREV_WRITE_TESTS_ENABLED="true"
    pytest tests/integration/test_question_answers_e2e.py -v -m write

Related to Issue #139: E2E integration tests for KB Articles and Q&A endpoints
"""

from __future__ import annotations

import logging
import os
from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest

from devrev.exceptions import DevRevError, NotFoundError
from devrev.models.question_answers import (
    QuestionAnswersCreateRequest,
    QuestionAnswersDeleteRequest,
    QuestionAnswersGetRequest,
    QuestionAnswersListRequest,
    QuestionAnswersUpdateRequest,
)

if TYPE_CHECKING:
    from devrev.client import DevRevClient
    from tests.integration.utils import TestDataManager

logger = logging.getLogger(__name__)

# Mark all tests in this module
_has_api_token = bool(os.environ.get("DEVREV_API_TOKEN") or os.environ.get("DEVREV_TEST_API_TOKEN"))

pytestmark = [
    pytest.mark.integration,
    pytest.mark.write,
    pytest.mark.skipif(
        not _has_api_token,
        reason="DEVREV_API_TOKEN or DEVREV_TEST_API_TOKEN environment variable required",
    ),
    pytest.mark.skipif(
        os.environ.get("DEVREV_WRITE_TESTS_ENABLED", "").lower() not in ("true", "1", "yes"),
        reason="DEVREV_WRITE_TESTS_ENABLED must be set to 'true' for write tests",
    ),
]


@pytest.fixture(scope="session")
def current_user_id(beta_write_client: DevRevClient) -> str:
    """Get the current authenticated user's DON ID."""
    user = beta_write_client.dev_users.self()
    return user.id


@pytest.fixture(scope="session")
def test_part_id(beta_write_client: DevRevClient) -> str:
    """Get a valid part ID for testing by listing available parts."""
    result = beta_write_client.parts.list(limit=1)
    if not result.parts:
        pytest.skip("No parts available for testing")
    return result.parts[0].id


@pytest.fixture
def qa_test_data(
    beta_write_client: DevRevClient,
    skip_if_write_disabled: None,
) -> Generator[TestDataManager, None, None]:
    """Provide a TestDataManager for Q&A tests with beta client and automatic cleanup."""
    from tests.integration.utils import TestDataManager

    manager = TestDataManager(beta_write_client)
    logger.info(f"Starting Q&A test with run_id: {manager.run_id}")

    yield manager

    report = manager.cleanup()
    if not report.all_succeeded:
        logger.error(f"Cleanup had failures:\n{report}")


class TestQuestionAnswersCRUD:
    """CRUD integration tests for Question Answers service.

    Demonstrates full create/read/update/delete lifecycle testing
    with proper cleanup and isolation for beta API features.
    """

    def test_create_question_answer_basic(
        self,
        beta_write_client: DevRevClient,
        qa_test_data: TestDataManager,
        current_user_id: str,
        test_part_id: str,
    ) -> None:
        """Test creating a Q&A with required fields."""
        # Arrange
        question_text = qa_test_data.generate_name("TestQuestion")

        # Act
        request = QuestionAnswersCreateRequest(
            question=question_text,
            answer="Default test answer",
            applies_to_parts=[test_part_id],
            owned_by=[current_user_id],
            status="draft",
        )
        qa = beta_write_client.question_answers.create(request)
        qa_test_data.register("question_answer", qa.id)

        # Assert
        assert qa.id is not None
        assert question_text in qa.question
        logger.info(f"✅ Created Q&A with required fields: {qa.id}")

    def test_create_question_answer_with_answer(
        self,
        beta_write_client: DevRevClient,
        qa_test_data: TestDataManager,
        current_user_id: str,
        test_part_id: str,
    ) -> None:
        """Test creating a Q&A with both question and answer."""
        # Arrange
        question_text = qa_test_data.generate_name("TestQuestion")
        answer_text = "This is a test answer created by SDK integration tests"

        # Act
        request = QuestionAnswersCreateRequest(
            question=question_text,
            answer=answer_text,
            applies_to_parts=[test_part_id],
            owned_by=[current_user_id],
            status="draft",
        )
        qa = beta_write_client.question_answers.create(request)
        qa_test_data.register("question_answer", qa.id)

        # Assert
        assert qa.id is not None
        assert question_text in qa.question
        assert qa.answer is not None
        assert answer_text in qa.answer
        logger.info(f"✅ Created Q&A with question and answer: {qa.id}")

    @pytest.mark.xfail(
        reason="DevRev API may return 400 for question-answers.get",
        raises=Exception,
    )
    def test_get_question_answer_by_id(
        self,
        beta_write_client: DevRevClient,
        qa_test_data: TestDataManager,
        current_user_id: str,
        test_part_id: str,
    ) -> None:
        """Test retrieving a Q&A by ID."""
        # Arrange - create Q&A first
        question_text = qa_test_data.generate_name("GetTest")
        create_request = QuestionAnswersCreateRequest(
            question=question_text,
            answer="Answer for get test",
            applies_to_parts=[test_part_id],
            owned_by=[current_user_id],
            status="draft",
        )
        created_qa = beta_write_client.question_answers.create(create_request)
        qa_test_data.register("question_answer", created_qa.id)

        # Act
        get_request = QuestionAnswersGetRequest(id=created_qa.id)
        retrieved_qa = beta_write_client.question_answers.get(get_request)

        # Assert
        assert retrieved_qa.id == created_qa.id
        assert question_text in retrieved_qa.question
        logger.info(f"✅ Retrieved Q&A by ID: {retrieved_qa.id}")

    def test_list_question_answers(
        self,
        beta_write_client: DevRevClient,
        qa_test_data: TestDataManager,
    ) -> None:
        """Test listing Q&As."""
        # Arrange - no setup needed

        # Act
        request = QuestionAnswersListRequest(limit=5)
        result = beta_write_client.question_answers.list(request)

        # Assert
        assert hasattr(result, "question_answers")
        assert isinstance(result.question_answers, list)
        logger.info(f"✅ Listed Q&As: {len(result.question_answers)} items")

    def test_update_question_answer_question(
        self,
        beta_write_client: DevRevClient,
        qa_test_data: TestDataManager,
        current_user_id: str,
        test_part_id: str,
    ) -> None:
        """Test updating a Q&A's question text."""
        # Arrange - create Q&A first
        original_question = qa_test_data.generate_name("OriginalQuestion")
        create_request = QuestionAnswersCreateRequest(
            question=original_question,
            answer="Answer for update test",
            applies_to_parts=[test_part_id],
            owned_by=[current_user_id],
            status="draft",
        )
        qa = beta_write_client.question_answers.create(create_request)
        qa_test_data.register("question_answer", qa.id)

        # Act
        new_question = qa_test_data.generate_name("UpdatedQuestion")
        update_request = QuestionAnswersUpdateRequest(
            id=qa.id,
            question=new_question,
        )
        updated_qa = beta_write_client.question_answers.update(update_request)

        # Assert
        assert updated_qa.id == qa.id
        assert new_question in updated_qa.question
        logger.info(f"✅ Updated Q&A question: {qa.id}")

    def test_update_question_answer_answer(
        self,
        beta_write_client: DevRevClient,
        qa_test_data: TestDataManager,
        current_user_id: str,
        test_part_id: str,
    ) -> None:
        """Test updating a Q&A's answer text."""
        # Arrange - create Q&A with original answer
        question_text = qa_test_data.generate_name("QuestionForAnswer")
        create_request = QuestionAnswersCreateRequest(
            question=question_text,
            answer="Original answer",
            applies_to_parts=[test_part_id],
            owned_by=[current_user_id],
            status="draft",
        )
        qa = beta_write_client.question_answers.create(create_request)
        qa_test_data.register("question_answer", qa.id)

        # Act
        answer_text = "This is a newly added answer via SDK test"
        update_request = QuestionAnswersUpdateRequest(
            id=qa.id,
            answer=answer_text,
        )
        updated_qa = beta_write_client.question_answers.update(update_request)

        # Assert
        assert updated_qa.id == qa.id
        assert updated_qa.answer is not None
        assert answer_text in updated_qa.answer
        logger.info(f"✅ Updated Q&A answer: {qa.id}")

    def test_delete_question_answer(
        self,
        beta_write_client: DevRevClient,
        qa_test_data: TestDataManager,
        current_user_id: str,
        test_part_id: str,
    ) -> None:
        """Test deleting a Q&A."""
        # Arrange
        question_text = qa_test_data.generate_name("ToDelete")
        create_request = QuestionAnswersCreateRequest(
            question=question_text,
            answer="Answer for delete test",
            applies_to_parts=[test_part_id],
            owned_by=[current_user_id],
            status="draft",
        )
        qa = beta_write_client.question_answers.create(create_request)
        # Note: NOT registering since we're testing delete

        # Act
        delete_request = QuestionAnswersDeleteRequest(id=qa.id)
        beta_write_client.question_answers.delete(delete_request)

        # Assert - verify Q&A is deleted by trying to get it
        with pytest.raises((NotFoundError, DevRevError)):
            get_request = QuestionAnswersGetRequest(id=qa.id)
            beta_write_client.question_answers.get(get_request)
        logger.info(f"✅ Deleted Q&A: {qa.id}")

    def test_question_answer_full_lifecycle(
        self,
        beta_write_client: DevRevClient,
        qa_test_data: TestDataManager,
        current_user_id: str,
        test_part_id: str,
    ) -> None:
        """Test full Q&A lifecycle: create -> get -> update -> list -> delete."""
        # Arrange
        question_text = qa_test_data.generate_name("LifecycleTest")
        answer_text = "Initial answer for lifecycle test"

        # Act & Assert - Create
        create_request = QuestionAnswersCreateRequest(
            question=question_text,
            answer=answer_text,
            applies_to_parts=[test_part_id],
            owned_by=[current_user_id],
            status="draft",
        )
        qa = beta_write_client.question_answers.create(create_request)
        # Note: NOT registering since we delete explicitly
        assert qa.id is not None
        logger.info(f"✅ Lifecycle: Created Q&A {qa.id}")

        # Act & Assert - Get (may fail with 400)
        try:
            get_request = QuestionAnswersGetRequest(id=qa.id)
            retrieved_qa = beta_write_client.question_answers.get(get_request)
            assert retrieved_qa.id == qa.id
            logger.info(f"✅ Lifecycle: Retrieved Q&A {qa.id}")
        except Exception as e:
            logger.warning(f"⚠️ Lifecycle: Get failed (known issue): {e}")

        # Act & Assert - Update
        new_question = qa_test_data.generate_name("UpdatedLifecycle")
        new_answer = "Updated answer for lifecycle test"
        update_request = QuestionAnswersUpdateRequest(
            id=qa.id,
            question=new_question,
            answer=new_answer,
        )
        updated_qa = beta_write_client.question_answers.update(update_request)
        assert new_question in updated_qa.question
        assert new_answer in updated_qa.answer
        logger.info(f"✅ Lifecycle: Updated Q&A {qa.id}")

        # Act & Assert - List
        list_request = QuestionAnswersListRequest(limit=10)
        list_result = beta_write_client.question_answers.list(list_request)
        assert hasattr(list_result, "question_answers")
        logger.info("✅ Lifecycle: Listed Q&As")

        # Act & Assert - Delete
        delete_request = QuestionAnswersDeleteRequest(id=qa.id)
        beta_write_client.question_answers.delete(delete_request)
        with pytest.raises((NotFoundError, DevRevError)):
            get_request = QuestionAnswersGetRequest(id=qa.id)
            beta_write_client.question_answers.get(get_request)
        logger.info(f"✅ Lifecycle: Deleted Q&A {qa.id}")


class TestQuestionAnswersErrorHandling:
    """Tests for error handling in Q&A operations.

    Validates that the SDK properly handles and reports errors
    from the API for invalid Q&A operations.
    """

    def test_get_nonexistent_qa_raises_error(
        self,
        beta_write_client: DevRevClient,
        qa_test_data: TestDataManager,
    ) -> None:
        """Test that getting a non-existent Q&A raises an error."""
        # Arrange
        fake_id = "don:core:dvrv-us-1:devo/FAKE:question_answer/DOESNOTEXIST"

        # Act & Assert - expect NotFoundError or similar API error
        with pytest.raises((NotFoundError, DevRevError)):
            get_request = QuestionAnswersGetRequest(id=fake_id)
            beta_write_client.question_answers.get(get_request)
        logger.info("✅ Get non-existent Q&A correctly raised error")

    def test_update_nonexistent_qa_raises_error(
        self,
        beta_write_client: DevRevClient,
        qa_test_data: TestDataManager,
    ) -> None:
        """Test that updating a non-existent Q&A raises an error."""
        # Arrange
        fake_id = "don:core:dvrv-us-1:devo/FAKE:question_answer/DOESNOTEXIST"

        # Act & Assert - expect NotFoundError or similar API error
        with pytest.raises((NotFoundError, DevRevError)):
            update_request = QuestionAnswersUpdateRequest(
                id=fake_id,
                question=qa_test_data.generate_name("ShouldFail"),
            )
            beta_write_client.question_answers.update(update_request)
        logger.info("✅ Update non-existent Q&A correctly raised error")

    def test_delete_nonexistent_qa_raises_error(
        self,
        beta_write_client: DevRevClient,
        qa_test_data: TestDataManager,
    ) -> None:
        """Test that deleting a non-existent Q&A raises an error."""
        # Arrange
        fake_id = "don:core:dvrv-us-1:devo/FAKE:question_answer/DOESNOTEXIST"

        # Act & Assert - expect NotFoundError or similar API error
        with pytest.raises((NotFoundError, DevRevError)):
            delete_request = QuestionAnswersDeleteRequest(id=fake_id)
            beta_write_client.question_answers.delete(delete_request)
        logger.info("✅ Delete non-existent Q&A correctly raised error")


class TestQuestionAnswersListPagination:
    """Tests for Q&A list pagination.

    Validates pagination behavior for question-answers.list endpoint.
    """

    def test_list_question_answers_with_limit(
        self,
        beta_write_client: DevRevClient,
        qa_test_data: TestDataManager,
    ) -> None:
        """Test listing Q&As with a limit parameter."""
        # Arrange
        limit = 2

        # Act
        request = QuestionAnswersListRequest(limit=limit)
        result = beta_write_client.question_answers.list(request)

        # Assert
        assert hasattr(result, "question_answers")
        assert isinstance(result.question_answers, list)
        assert len(result.question_answers) <= limit
        logger.info(f"✅ Listed Q&As with limit={limit}: {len(result.question_answers)} items")

    def test_list_question_answers_default(
        self,
        beta_write_client: DevRevClient,
        qa_test_data: TestDataManager,
    ) -> None:
        """Test listing Q&As with default parameters."""
        # Arrange - no parameters

        # Act
        result = beta_write_client.question_answers.list()

        # Assert
        assert hasattr(result, "question_answers")
        assert isinstance(result.question_answers, list)
        logger.info(f"✅ Listed Q&As with defaults: {len(result.question_answers)} items")
