"""Integration tests for Phase 2: Extended Services.

This test suite adds coverage for:
- code-changes.list, code-changes.get
- brands.list, brands.get
- engagements.list, engagements.get, engagements.count
- incidents.list, incidents.get
- uoms.list, uoms.get, uoms.count
- question-answers.list, question-answers.get
- preferences.get

Related to Issue #103: Achieve 100% Integration Test Coverage
"""

import logging

import pytest

from devrev import DevRevClient
from devrev.models.code_changes import CodeChangesListRequest, CodeChangesGetRequest
from devrev.models.brands import BrandsListRequest, BrandsGetRequest
from devrev.models.question_answers import QuestionAnswersListRequest, QuestionAnswersGetRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def client() -> DevRevClient:
    """Create a DevRev client for integration tests."""
    return DevRevClient()


class TestCodeChangesEndpoints:
    """Tests for code-changes endpoints."""

    def test_code_changes_list(self, client: DevRevClient) -> None:
        """Test code-changes.list endpoint."""
        result = client.code_changes.list()
        assert isinstance(result, list)
        logger.info(f"✅ code-changes.list: {len(result)} code changes")

    def test_code_changes_get(self, client: DevRevClient) -> None:
        """Test code-changes.get endpoint."""
        list_result = client.code_changes.list()
        if not list_result or len(list_result) == 0:
            pytest.skip("No code changes available for testing")
        
        code_change_id = list_result[0].id
        
        request = CodeChangesGetRequest(id=code_change_id)
        result = client.code_changes.get(request)
        assert result.id == code_change_id
        logger.info(f"✅ code-changes.get: {result.id}")


class TestBrandsEndpoints:
    """Tests for brands endpoints."""

    def test_brands_list(self, client: DevRevClient) -> None:
        """Test brands.list endpoint."""
        result = client.brands.list()
        assert hasattr(result, "brands")
        assert isinstance(result.brands, list)
        logger.info(f"✅ brands.list: {len(result.brands)} brands")

    def test_brands_get(self, client: DevRevClient) -> None:
        """Test brands.get endpoint."""
        list_result = client.brands.list()
        if not list_result.brands:
            pytest.skip("No brands available for testing")
        
        brand_id = list_result.brands[0].id
        
        result = client.brands.get(brand_id)
        assert result.id == brand_id
        assert hasattr(result, "name")
        logger.info(f"✅ brands.get: {result.name}")


class TestEngagementsEndpoints:
    """Tests for engagements endpoints."""

    def test_engagements_list(self, client: DevRevClient) -> None:
        """Test engagements.list endpoint."""
        result = client.engagements.list(limit=5)
        assert hasattr(result, "engagements")
        assert isinstance(result.engagements, list)
        logger.info(f"✅ engagements.list: {len(result.engagements)} engagements")

    def test_engagements_get(self, client: DevRevClient) -> None:
        """Test engagements.get endpoint."""
        list_result = client.engagements.list(limit=1)
        if not list_result.engagements:
            pytest.skip("No engagements available for testing")
        
        engagement_id = list_result.engagements[0].id
        
        result = client.engagements.get(engagement_id)
        assert result.id == engagement_id
        logger.info(f"✅ engagements.get: {result.id}")

    def test_engagements_count(self, client: DevRevClient) -> None:
        """Test engagements.count endpoint."""
        result = client.engagements.count()
        assert isinstance(result, int)
        assert result >= 0
        logger.info(f"✅ engagements.count: {result} engagements")


class TestIncidentsEndpoints:
    """Tests for incidents endpoints."""

    def test_incidents_list(self, client: DevRevClient) -> None:
        """Test incidents.list endpoint."""
        result = client.incidents.list(limit=5)
        assert hasattr(result, "incidents")
        assert isinstance(result.incidents, list)
        logger.info(f"✅ incidents.list: {len(result.incidents)} incidents")

    def test_incidents_get(self, client: DevRevClient) -> None:
        """Test incidents.get endpoint."""
        list_result = client.incidents.list(limit=1)
        if not list_result.incidents:
            pytest.skip("No incidents available for testing")
        
        incident_id = list_result.incidents[0].id
        
        result = client.incidents.get(incident_id)
        assert result.id == incident_id
        logger.info(f"✅ incidents.get: {result.id}")


class TestUomsEndpoints:
    """Tests for uoms endpoints."""

    def test_uoms_list(self, client: DevRevClient) -> None:
        """Test uoms.list endpoint."""
        result = client.uoms.list(limit=5)
        assert hasattr(result, "uoms")
        assert isinstance(result.uoms, list)
        logger.info(f"✅ uoms.list: {len(result.uoms)} UOMs")

    def test_uoms_get(self, client: DevRevClient) -> None:
        """Test uoms.get endpoint."""
        list_result = client.uoms.list(limit=1)
        if not list_result.uoms:
            pytest.skip("No UOMs available for testing")

        uom_id = list_result.uoms[0].id

        result = client.uoms.get(uom_id)
        assert result.id == uom_id
        logger.info(f"✅ uoms.get: {result.id}")

    def test_uoms_count(self, client: DevRevClient) -> None:
        """Test uoms.count endpoint."""
        result = client.uoms.count()
        assert isinstance(result, int)
        assert result >= 0
        logger.info(f"✅ uoms.count: {result} UOMs")


class TestQuestionAnswersEndpoints:
    """Tests for question-answers endpoints."""

    def test_question_answers_list(self, client: DevRevClient) -> None:
        """Test question-answers.list endpoint."""
        result = client.question_answers.list()
        assert hasattr(result, "question_answers")
        assert isinstance(result.question_answers, list)
        logger.info(f"✅ question-answers.list: {len(result.question_answers)} Q&As")

    def test_question_answers_get(self, client: DevRevClient) -> None:
        """Test question-answers.get endpoint."""
        list_result = client.question_answers.list()
        if not list_result.question_answers:
            pytest.skip("No question answers available for testing")

        qa_id = list_result.question_answers[0].id

        request = QuestionAnswersGetRequest(id=qa_id)
        result = client.question_answers.get(request)
        assert result.id == qa_id
        logger.info(f"✅ question-answers.get: {result.id}")


class TestPreferencesEndpoints:
    """Tests for preferences endpoints."""

    def test_preferences_get(self, client: DevRevClient) -> None:
        """Test preferences.get endpoint."""
        # Get current user's preferences
        result = client.preferences.get()
        assert result is not None
        logger.info(f"✅ preferences.get: Retrieved user preferences")

