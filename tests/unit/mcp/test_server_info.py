"""Tests for DevRev MCP server info tool and resource."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestServerInfoResource:
    """Tests for the devrev://server/info resource."""

    @pytest.mark.asyncio
    async def test_returns_valid_json(self):
        """Test that the resource returns valid JSON."""
        from devrev_mcp.resources.server_info import get_server_info_resource

        result = await get_server_info_resource()
        data = json.loads(result)
        assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_contains_required_fields(self):
        """Test that the resource contains all required fields."""
        from devrev_mcp.resources.server_info import get_server_info_resource

        result = await get_server_info_resource()
        data = json.loads(result)
        assert data["uri"] == "devrev://server/info"
        assert data["type"] == "server_info"
        assert "version" in data
        assert "python_version" in data
        assert "platform" in data
        assert "links" in data
        assert "note" in data

    @pytest.mark.asyncio
    async def test_links_contain_urls(self):
        """Test that links contain expected URLs."""
        from devrev_mcp.resources.server_info import get_server_info_resource

        result = await get_server_info_resource()
        data = json.loads(result)
        assert "github" in data["links"]
        assert "documentation" in data["links"]
        assert "pypi" in data["links"]
        assert data["links"]["github"].startswith("https://")

    @pytest.mark.asyncio
    async def test_version_matches_package(self):
        """Test that the version matches the package version."""
        from devrev_mcp import __version__
        from devrev_mcp.resources.server_info import get_server_info_resource

        result = await get_server_info_resource()
        data = json.loads(result)
        assert data["version"] == __version__

    @pytest.mark.asyncio
    async def test_python_version_format(self):
        """Test that python_version is in X.Y.Z format."""
        from devrev_mcp.resources.server_info import get_server_info_resource

        result = await get_server_info_resource()
        data = json.loads(result)
        parts = data["python_version"].split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    @pytest.mark.asyncio
    async def test_note_mentions_tool(self):
        """Test that the note directs users to the tool for dynamic info."""
        from devrev_mcp.resources.server_info import get_server_info_resource

        result = await get_server_info_resource()
        data = json.loads(result)
        assert "devrev_server_info" in data["note"]


class TestServerInfoTool:
    """Tests for the devrev_server_info tool."""

    @pytest.mark.asyncio
    async def test_returns_server_section(self, mock_ctx):
        """Test that the tool returns server information."""
        from devrev_mcp.tools.server_info import devrev_server_info

        with (
            patch(
                "devrev_mcp.tools.server_info._fetch_latest_pypi_version",
                new_callable=AsyncMock,
                return_value="2.6.0",
            ),
            patch("devrev_mcp.middleware.health._start_time", 0.0),
        ):
            result = await devrev_server_info(mock_ctx)

        assert "server" in result
        assert "version" in result["server"]
        assert "name" in result["server"]
        assert "uptime_seconds" in result["server"]
        assert "python_version" in result["server"]
        assert "platform" in result["server"]

    @pytest.mark.asyncio
    async def test_returns_capabilities_section(self, mock_ctx):
        """Test that the tool returns capabilities information."""
        from devrev_mcp.tools.server_info import devrev_server_info

        with patch(
            "devrev_mcp.tools.server_info._fetch_latest_pypi_version",
            new_callable=AsyncMock,
            return_value="2.6.0",
        ):
            result = await devrev_server_info(mock_ctx)

        assert "capabilities" in result
        caps = result["capabilities"]
        assert "beta_tools_enabled" in caps
        assert "destructive_tools_enabled" in caps
        assert "auth_mode" in caps
        assert "transport" in caps
        assert "audit_logging" in caps
        assert "rate_limit_rpm" in caps

    @pytest.mark.asyncio
    async def test_returns_update_status_section(self, mock_ctx):
        """Test that the tool returns update status information."""
        from devrev_mcp.tools.server_info import devrev_server_info

        with patch(
            "devrev_mcp.tools.server_info._fetch_latest_pypi_version",
            new_callable=AsyncMock,
            return_value="2.6.0",
        ):
            result = await devrev_server_info(mock_ctx)

        assert "update_status" in result
        status = result["update_status"]
        assert "current_version" in status
        assert "latest_version" in status
        assert "is_latest" in status
        assert "pypi_package" in status

    @pytest.mark.asyncio
    async def test_returns_links_section(self, mock_ctx):
        """Test that the tool returns links."""
        from devrev_mcp.tools.server_info import devrev_server_info

        with patch(
            "devrev_mcp.tools.server_info._fetch_latest_pypi_version",
            new_callable=AsyncMock,
            return_value="2.6.0",
        ):
            result = await devrev_server_info(mock_ctx)

        assert "links" in result
        assert "github" in result["links"]
        assert "documentation" in result["links"]
        assert "pypi" in result["links"]

    @pytest.mark.asyncio
    async def test_pypi_failure_returns_unknown(self, mock_ctx):
        """Test graceful handling when PyPI is unreachable."""
        from devrev_mcp.tools.server_info import devrev_server_info

        with patch(
            "devrev_mcp.tools.server_info._fetch_latest_pypi_version",
            new_callable=AsyncMock,
            return_value=None,
        ):
            result = await devrev_server_info(mock_ctx)

        assert result["update_status"]["latest_version"] == "unknown"
        assert result["update_status"]["is_latest"] is None

    @pytest.mark.asyncio
    async def test_is_latest_true_when_current_equals_latest(self, mock_ctx):
        """Test is_latest is True when versions match."""
        from devrev_mcp import __version__
        from devrev_mcp.tools.server_info import devrev_server_info

        with patch(
            "devrev_mcp.tools.server_info._fetch_latest_pypi_version",
            new_callable=AsyncMock,
            return_value=__version__,
        ):
            result = await devrev_server_info(mock_ctx)

        assert result["update_status"]["is_latest"] is True

    @pytest.mark.asyncio
    async def test_is_latest_false_when_behind(self, mock_ctx):
        """Test is_latest is False when a newer version exists."""
        from devrev_mcp.tools.server_info import devrev_server_info

        with patch(
            "devrev_mcp.tools.server_info._fetch_latest_pypi_version",
            new_callable=AsyncMock,
            return_value="99.99.99",
        ):
            result = await devrev_server_info(mock_ctx)

        assert result["update_status"]["is_latest"] is False


class TestVersionComparison:
    """Tests for the _compare_versions helper."""

    def test_equal_versions(self):
        from devrev_mcp.tools.server_info import _compare_versions

        assert _compare_versions("2.6.0", "2.6.0") is True

    def test_current_newer(self):
        from devrev_mcp.tools.server_info import _compare_versions

        assert _compare_versions("2.7.0", "2.6.0") is True

    def test_current_older(self):
        from devrev_mcp.tools.server_info import _compare_versions

        assert _compare_versions("2.5.0", "2.6.0") is False

    def test_major_version_difference(self):
        from devrev_mcp.tools.server_info import _compare_versions

        assert _compare_versions("3.0.0", "2.99.99") is True
        assert _compare_versions("1.99.99", "2.0.0") is False

    def test_invalid_version_returns_none(self):
        """Test that invalid versions return None when packaging is not available."""
        import sys
        from unittest.mock import patch

        from devrev_mcp.tools.server_info import _compare_versions

        # Mock ImportError to force fallback to simple comparison
        # We need to patch the import at the point where it's used
        with patch.dict(sys.modules, {"packaging.version": None}):
            result = _compare_versions("invalid", "also-invalid")
            assert result is None

    def test_invalid_version_with_packaging_raises(self):
        """Test that invalid versions raise InvalidVersion when packaging is available."""
        from packaging.version import InvalidVersion

        from devrev_mcp.tools.server_info import _compare_versions

        # When packaging is available, invalid versions should raise
        with pytest.raises(InvalidVersion):
            _compare_versions("invalid", "also-invalid")


class TestFetchLatestPyPIVersion:
    """Tests for the _fetch_latest_pypi_version helper."""

    @pytest.mark.asyncio
    async def test_successful_fetch(self):
        """Test successful PyPI version fetch."""
        from devrev_mcp.tools.server_info import _fetch_latest_pypi_version

        mock_response = MagicMock()
        mock_response.json.return_value = {"info": {"version": "2.6.0"}}
        mock_response.raise_for_status = MagicMock()

        with patch("devrev_mcp.tools.server_info.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_client

            result = await _fetch_latest_pypi_version()
            assert result == "2.6.0"

    @pytest.mark.asyncio
    async def test_network_error_returns_none(self):
        """Test that network errors return None."""
        from devrev_mcp.tools.server_info import _fetch_latest_pypi_version

        with patch("devrev_mcp.tools.server_info.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=Exception("Network error"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_client

            result = await _fetch_latest_pypi_version()
            assert result is None

    @pytest.mark.asyncio
    async def test_malformed_response_returns_none(self):
        """Test that malformed JSON responses return None gracefully."""
        from devrev_mcp.tools.server_info import _fetch_latest_pypi_version

        mock_response = MagicMock()
        mock_response.json.return_value = {}  # Missing 'info' key
        mock_response.raise_for_status = MagicMock()

        with patch("devrev_mcp.tools.server_info.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_client

            result = await _fetch_latest_pypi_version()
            assert result is None  # .get("info", {}).get("version") returns None


class TestServerInstructions:
    """Tests for the server instructions parameter."""

    def test_mcp_server_has_instructions(self):
        """Test that the MCP server instance has instructions set."""
        import os
        from unittest.mock import patch as mock_patch

        with mock_patch.dict(os.environ, {"DEVREV_API_TOKEN": "test-token"}, clear=False):
            from devrev_mcp.server import mcp

            # FastMCP stores instructions - check it's set and contains version info
            assert mcp.instructions is not None
            assert "DevRev MCP Server" in mcp.instructions
            assert "devrev_server_info" in mcp.instructions

    def test_instructions_contain_version(self):
        """Test that instructions include the version string."""
        import os
        from unittest.mock import patch as mock_patch

        with mock_patch.dict(os.environ, {"DEVREV_API_TOKEN": "test-token"}, clear=False):
            from devrev_mcp import __version__
            from devrev_mcp.server import mcp

            assert __version__ in mcp.instructions
