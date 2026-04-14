"""Unit tests for Rev Orgs models and service."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import httpx
import pytest
from pydantic import ValidationError

from devrev.models.rev_orgs import (
    RevOrg,
    RevOrgsCreateRequest,
    RevOrgsDeleteRequest,
    RevOrgsGetRequest,
    RevOrgsGetResponse,
    RevOrgsListRequest,
    RevOrgsListResponse,
    RevOrgSummary,
    RevOrgsUpdateRequest,
)
from devrev.services.rev_orgs import RevOrgsService

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def create_mock_response(data: dict[str, Any], status_code: int = 200) -> MagicMock:
    """Create a mock HTTP response."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.is_success = 200 <= status_code < 300
    response.content = b"{}"  # truthy so _post reads response.json()
    response.json.return_value = data
    return response


@pytest.fixture
def mock_http_client() -> MagicMock:
    """Sync mock HTTP client."""
    return MagicMock()


@pytest.fixture
def sample_rev_org_data() -> dict[str, Any]:
    """Minimal Rev Org data matching the API response shape."""
    return {
        "id": "don:core:dvrv-us-1:devo/1:revo/123",
        "display_id": "REV-123",
        "display_name": "Acme Corp",
    }


@pytest.fixture
def full_rev_org_data(sample_rev_org_data: dict[str, Any]) -> dict[str, Any]:
    """Rev Org data with all optional fields populated."""
    return {
        **sample_rev_org_data,
        "description": "Primary org for Acme",
        "account": {
            "id": "don:core:dvrv-us-1:devo/1:account/42",
            "display_name": "Acme Account",
        },
        "created_date": "2024-01-15T10:00:00Z",
        "modified_date": "2024-06-01T08:30:00Z",
        "created_by": {"id": "don:identity:dvrv-us-1:devo/1:devu/7"},
        "modified_by": {"id": "don:identity:dvrv-us-1:devo/1:devu/7"},
        "domain": "acme.example.com",
        "external_ref": "ext-acme-001",
        "external_refs": ["ext-acme-001", "crm-9999"],
        "custom_fields": {"key": "value"},
        "sub_type": "enterprise",
        "tier": "gold",
        "artifacts": ["don:core:artifact:1"],
    }


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


class TestRevOrgModels:
    """Tests for Rev Org Pydantic models."""

    def test_rev_org_model_creation(self, sample_rev_org_data: dict[str, Any]) -> None:
        """RevOrg can be created with only the required id field."""
        rev_org = RevOrg.model_validate({"id": "don:core:dvrv-us-1:devo/1:revo/1"})

        assert rev_org.id == "don:core:dvrv-us-1:devo/1:revo/1"
        assert rev_org.display_name is None
        assert rev_org.account is None

    def test_rev_org_model_all_fields(self, full_rev_org_data: dict[str, Any]) -> None:
        """RevOrg parses all optional fields correctly."""
        rev_org = RevOrg.model_validate(full_rev_org_data)

        assert rev_org.id == full_rev_org_data["id"]
        assert rev_org.display_name == "Acme Corp"
        assert rev_org.description == "Primary org for Acme"
        assert rev_org.account is not None
        assert rev_org.account.id == "don:core:dvrv-us-1:devo/1:account/42"
        assert rev_org.domain == "acme.example.com"
        assert rev_org.external_ref == "ext-acme-001"
        assert rev_org.external_refs == ["ext-acme-001", "crm-9999"]
        assert rev_org.custom_fields == {"key": "value"}
        assert rev_org.tier == "gold"
        assert rev_org.artifacts == ["don:core:artifact:1"]
        assert rev_org.created_date is not None
        assert rev_org.modified_date is not None

    def test_rev_org_summary_model(self) -> None:
        """RevOrgSummary parses id and optional display fields."""
        summary = RevOrgSummary.model_validate(
            {
                "id": "don:core:dvrv-us-1:devo/1:revo/99",
                "display_id": "REV-99",
                "display_name": "Summary Org",
            }
        )

        assert summary.id == "don:core:dvrv-us-1:devo/1:revo/99"
        assert summary.display_id == "REV-99"
        assert summary.display_name == "Summary Org"

    def test_rev_orgs_get_request(self) -> None:
        """RevOrgsGetRequest serializes id correctly."""
        req = RevOrgsGetRequest(id="don:core:dvrv-us-1:devo/1:revo/5")
        data = req.model_dump(exclude_none=True)

        assert data["id"] == "don:core:dvrv-us-1:devo/1:revo/5"

    def test_rev_orgs_list_request_defaults(self) -> None:
        """RevOrgsListRequest has all-None defaults."""
        req = RevOrgsListRequest()
        data = req.model_dump(exclude_none=True)

        assert data == {}

    @pytest.mark.parametrize(
        "account_ids, limit",
        [
            (["don:core:account:1"], 10),
            (["don:core:account:1", "don:core:account:2"], 50),
        ],
    )
    def test_rev_orgs_list_request_with_filters(self, account_ids: list[str], limit: int) -> None:
        """RevOrgsListRequest serializes account and limit filters."""
        req = RevOrgsListRequest(account=account_ids, limit=limit)
        data = req.model_dump(exclude_none=True)

        assert data["account"] == account_ids
        assert data["limit"] == limit

    def test_rev_orgs_create_request(self) -> None:
        """RevOrgsCreateRequest accepts required display_name and account."""
        req = RevOrgsCreateRequest(
            display_name="New Org",
            account="don:core:dvrv-us-1:devo/1:account/1",
        )

        assert req.display_name == "New Org"
        assert req.account == "don:core:dvrv-us-1:devo/1:account/1"
        assert req.description is None

    def test_rev_orgs_create_request_validation(self) -> None:
        """RevOrgsCreateRequest enforces display_name min_length=1."""
        with pytest.raises(ValidationError):
            RevOrgsCreateRequest(
                display_name="",
                account="don:core:dvrv-us-1:devo/1:account/1",
            )

    def test_rev_orgs_update_request(self) -> None:
        """RevOrgsUpdateRequest requires id."""
        req = RevOrgsUpdateRequest(id="don:core:dvrv-us-1:devo/1:revo/7", display_name="Renamed")
        assert req.id == "don:core:dvrv-us-1:devo/1:revo/7"
        assert req.display_name == "Renamed"

        with pytest.raises(ValidationError):
            RevOrgsUpdateRequest()  # type: ignore[call-arg]

    def test_rev_orgs_delete_request(self) -> None:
        """RevOrgsDeleteRequest requires id."""
        req = RevOrgsDeleteRequest(id="don:core:dvrv-us-1:devo/1:revo/8")
        assert req.id == "don:core:dvrv-us-1:devo/1:revo/8"

        with pytest.raises(ValidationError):
            RevOrgsDeleteRequest()  # type: ignore[call-arg]

    def test_rev_orgs_get_response(self, sample_rev_org_data: dict[str, Any]) -> None:
        """RevOrgsGetResponse deserializes a get response."""
        response = RevOrgsGetResponse.model_validate({"rev_org": sample_rev_org_data})

        assert isinstance(response.rev_org, RevOrg)
        assert response.rev_org.id == sample_rev_org_data["id"]
        assert response.rev_org.display_name == "Acme Corp"

    def test_rev_orgs_list_response(self, sample_rev_org_data: dict[str, Any]) -> None:
        """RevOrgsListResponse deserializes list and pagination cursor."""
        response = RevOrgsListResponse.model_validate(
            {
                "rev_orgs": [
                    sample_rev_org_data,
                    {**sample_rev_org_data, "id": "don:core:revo/456"},
                ],
                "next_cursor": "cursor-abc",
            }
        )

        assert len(response.rev_orgs) == 2
        assert all(isinstance(r, RevOrg) for r in response.rev_orgs)
        assert response.next_cursor == "cursor-abc"


# ---------------------------------------------------------------------------
# Service tests
# ---------------------------------------------------------------------------


class TestRevOrgsService:
    """Tests for RevOrgsService (mocked HTTP)."""

    def test_rev_orgs_service_get(
        self,
        mock_http_client: MagicMock,
        sample_rev_org_data: dict[str, Any],
    ) -> None:
        """get() calls /rev-orgs.get and returns a RevOrg."""
        mock_http_client.post.return_value = create_mock_response({"rev_org": sample_rev_org_data})

        service = RevOrgsService(mock_http_client)
        result = service.get("don:core:dvrv-us-1:devo/1:revo/123")

        assert isinstance(result, RevOrg)
        assert result.id == sample_rev_org_data["id"]
        mock_http_client.post.assert_called_once()
        call_endpoint = mock_http_client.post.call_args[0][0]
        assert call_endpoint == "/rev-orgs.get"

    def test_rev_orgs_service_list(
        self,
        mock_http_client: MagicMock,
        sample_rev_org_data: dict[str, Any],
    ) -> None:
        """list() calls /rev-orgs.list and returns RevOrgsListResponse."""
        mock_http_client.post.return_value = create_mock_response(
            {"rev_orgs": [sample_rev_org_data]}
        )

        service = RevOrgsService(mock_http_client)
        result = service.list()

        assert isinstance(result, RevOrgsListResponse)
        assert len(result.rev_orgs) == 1
        assert isinstance(result.rev_orgs[0], RevOrg)
        mock_http_client.post.assert_called_once()
        call_endpoint = mock_http_client.post.call_args[0][0]
        assert call_endpoint == "/rev-orgs.list"

    def test_rev_orgs_service_list_with_filters(
        self,
        mock_http_client: MagicMock,
        sample_rev_org_data: dict[str, Any],
    ) -> None:
        """list() passes account and limit filters to the endpoint."""
        mock_http_client.post.return_value = create_mock_response(
            {"rev_orgs": [sample_rev_org_data]}
        )

        service = RevOrgsService(mock_http_client)
        result = service.list(
            account=["don:core:dvrv-us-1:devo/1:account/1"],
            limit=25,
        )

        assert isinstance(result, RevOrgsListResponse)
        mock_http_client.post.assert_called_once()
        call_kwargs = mock_http_client.post.call_args[1]
        assert call_kwargs["data"]["account"] == ["don:core:dvrv-us-1:devo/1:account/1"]
        assert call_kwargs["data"]["limit"] == 25

    def test_rev_orgs_service_create(
        self,
        mock_http_client: MagicMock,
        sample_rev_org_data: dict[str, Any],
    ) -> None:
        """create() calls /rev-orgs.create with the correct payload."""
        mock_http_client.post.return_value = create_mock_response({"rev_org": sample_rev_org_data})

        service = RevOrgsService(mock_http_client)
        result = service.create(
            display_name="Acme Corp",
            account="don:core:dvrv-us-1:devo/1:account/42",
            description="Primary org",
            tier="gold",
        )

        assert isinstance(result, RevOrg)
        assert result.id == sample_rev_org_data["id"]
        mock_http_client.post.assert_called_once()
        call_endpoint = mock_http_client.post.call_args[0][0]
        assert call_endpoint == "/rev-orgs.create"
        payload = mock_http_client.post.call_args[1]["data"]
        assert payload["display_name"] == "Acme Corp"
        assert payload["account"] == "don:core:dvrv-us-1:devo/1:account/42"
        assert payload["description"] == "Primary org"
        assert payload["tier"] == "gold"

    def test_rev_orgs_service_update(
        self,
        mock_http_client: MagicMock,
        sample_rev_org_data: dict[str, Any],
    ) -> None:
        """update() calls /rev-orgs.update with id and changed fields."""
        updated = {**sample_rev_org_data, "display_name": "Acme Corp Renamed"}
        mock_http_client.post.return_value = create_mock_response({"rev_org": updated})

        service = RevOrgsService(mock_http_client)
        result = service.update(
            "don:core:dvrv-us-1:devo/1:revo/123",
            display_name="Acme Corp Renamed",
        )

        assert isinstance(result, RevOrg)
        assert result.display_name == "Acme Corp Renamed"
        mock_http_client.post.assert_called_once()
        call_endpoint = mock_http_client.post.call_args[0][0]
        assert call_endpoint == "/rev-orgs.update"
        payload = mock_http_client.post.call_args[1]["data"]
        assert payload["id"] == "don:core:dvrv-us-1:devo/1:revo/123"
        assert payload["display_name"] == "Acme Corp Renamed"

    def test_rev_orgs_service_delete(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """delete() calls /rev-orgs.delete and returns None."""
        mock_http_client.post.return_value = create_mock_response({})

        service = RevOrgsService(mock_http_client)
        result = service.delete("don:core:dvrv-us-1:devo/1:revo/123")

        assert result is None
        mock_http_client.post.assert_called_once()
        call_endpoint = mock_http_client.post.call_args[0][0]
        assert call_endpoint == "/rev-orgs.delete"
        payload = mock_http_client.post.call_args[1]["data"]
        assert payload["id"] == "don:core:dvrv-us-1:devo/1:revo/123"
