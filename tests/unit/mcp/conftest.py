"""MCP-specific test fixtures.

This module provides pytest fixtures for testing MCP tools that interact with
the DevRev API through the AsyncDevRevClient.

The fixtures simulate the MCP server context structure where tools receive a
Context object with access to the AppContext (containing the client and config).

Example usage:
    ```python
    async def test_works_list(mock_ctx, mock_client):
        # Configure mock response
        mock_client.works.list.return_value = {
            "works": [{"id": "work-1", "title": "Test"}],
            "count": 1
        }

        # Call the MCP tool
        result = await devrev_works_list(mock_ctx, query="test")

        # Verify the result
        assert result["count"] == 1
        mock_client.works.list.assert_called_once()
    ```
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_client():
    """Create a mock AsyncDevRevClient with all service properties.

    Returns:
        AsyncMock: A mock client with the following services:
            - works: Work items service (list, get, create, update, delete, count, export)
            - accounts: Accounts service (list, get, create, update, delete, merge)
            - dev_users: Dev users service (list, get)
            - rev_users: Rev users service (list, get, create)
            - search: Search service (hybrid, core)
            - recommendations: Recommendations service (get_reply, chat_completions)
            - close: Async close method
    """
    client = AsyncMock()

    # Works service
    client.works = AsyncMock()
    client.works.list = AsyncMock()
    client.works.get = AsyncMock()
    client.works.create = AsyncMock()
    client.works.update = AsyncMock()
    client.works.delete = AsyncMock()
    client.works.count = AsyncMock()
    client.works.export = AsyncMock()

    # Accounts service
    client.accounts = AsyncMock()
    client.accounts.list = AsyncMock()
    client.accounts.get = AsyncMock()
    client.accounts.create = AsyncMock()
    client.accounts.update = AsyncMock()
    client.accounts.delete = AsyncMock()
    client.accounts.merge = AsyncMock()

    # Dev users service
    client.dev_users = AsyncMock()
    client.dev_users.list = AsyncMock()
    client.dev_users.get = AsyncMock()

    # Rev users service
    client.rev_users = AsyncMock()
    client.rev_users.list = AsyncMock()
    client.rev_users.get = AsyncMock()
    client.rev_users.create = AsyncMock()

    # Search service (beta)
    client.search = AsyncMock()
    client.search.hybrid = AsyncMock()
    client.search.core = AsyncMock()

    # Recommendations service (beta)
    client.recommendations = AsyncMock()
    client.recommendations.get_reply = AsyncMock()
    client.recommendations.chat_completions = AsyncMock()

    # Close method
    client.close = AsyncMock()

    return client


@pytest.fixture
def mcp_config():
    """Create an MCPServerConfig instance with test defaults.

    Sets DEVREV_API_TOKEN environment variable to prevent SDK config errors.

    Returns:
        MCPServerConfig: Configuration instance for the MCP server.
    """
    with patch.dict(os.environ, {"DEVREV_API_TOKEN": "test-token"}, clear=False):
        from devrev_mcp.config import MCPServerConfig

        return MCPServerConfig()


@pytest.fixture
def app_context(mock_client, mcp_config):
    """Create an AppContext with mock client and config.

    Args:
        mock_client: The mock AsyncDevRevClient fixture.
        mcp_config: The MCPServerConfig fixture.

    Returns:
        AppContext: Application context containing the mock client and config.
    """
    from devrev_mcp.server import AppContext

    return AppContext(client=mock_client, config=mcp_config)


@pytest.fixture
def mock_ctx(app_context):
    """Create a mock MCP Context object.

    The Context object simulates the structure used by FastMCP tools:
    - ctx.request_context.lifespan_context -> AppContext

    Args:
        app_context: The AppContext fixture.

    Returns:
        MagicMock: A mock Context with request_context.lifespan_context set to app_context.
    """
    ctx = MagicMock()
    ctx.request_context.lifespan_context = app_context
    return ctx
