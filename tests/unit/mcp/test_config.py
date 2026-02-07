"""Unit tests for MCP server configuration."""

import os
from unittest.mock import patch

from devrev_mcp.config import MCPServerConfig


class TestMCPServerConfig:
    """Tests for MCPServerConfig class."""

    def test_default_values(self) -> None:
        """Test that config loads with all default values."""
        # Clear any existing MCP_ env vars
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}

        with patch.dict(os.environ, env_vars, clear=True):
            config = MCPServerConfig()

            assert config.server_name == "DevRev MCP Server"
            assert config.log_level == "INFO"
            assert config.enable_beta_tools is True
            assert config.default_page_size == 25
            assert config.max_page_size == 100

    def test_env_override_log_level(self) -> None:
        """Test that MCP_LOG_LEVEL environment variable overrides default."""
        # Clear existing MCP_ vars and set MCP_LOG_LEVEL
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_LOG_LEVEL"] = "DEBUG"

        with patch.dict(os.environ, env_vars, clear=True):
            config = MCPServerConfig()

            assert config.log_level == "DEBUG"
            # Other values should remain default
            assert config.server_name == "DevRev MCP Server"
            assert config.enable_beta_tools is True

    def test_env_override_enable_beta_tools(self) -> None:
        """Test that MCP_ENABLE_BETA_TOOLS=false disables beta tools."""
        # Clear existing MCP_ vars and set MCP_ENABLE_BETA_TOOLS
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_ENABLE_BETA_TOOLS"] = "false"

        with patch.dict(os.environ, env_vars, clear=True):
            config = MCPServerConfig()

            assert config.enable_beta_tools is False
            # Other values should remain default
            assert config.server_name == "DevRev MCP Server"
            assert config.log_level == "INFO"

    def test_env_override_page_sizes(self) -> None:
        """Test that MCP_DEFAULT_PAGE_SIZE and MCP_MAX_PAGE_SIZE can be overridden."""
        # Clear existing MCP_ vars and set page size vars
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_DEFAULT_PAGE_SIZE"] = "50"
        env_vars["MCP_MAX_PAGE_SIZE"] = "200"

        with patch.dict(os.environ, env_vars, clear=True):
            config = MCPServerConfig()

            assert config.default_page_size == 50
            assert config.max_page_size == 200
            # Other values should remain default
            assert config.server_name == "DevRev MCP Server"
            assert config.log_level == "INFO"
            assert config.enable_beta_tools is True

    def test_env_override_server_name(self) -> None:
        """Test that MCP_SERVER_NAME can be overridden."""
        # Clear existing MCP_ vars and set server name
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_SERVER_NAME"] = "Custom MCP Server"

        with patch.dict(os.environ, env_vars, clear=True):
            config = MCPServerConfig()

            assert config.server_name == "Custom MCP Server"
            # Other values should remain default
            assert config.log_level == "INFO"
            assert config.enable_beta_tools is True

    def test_multiple_env_overrides(self) -> None:
        """Test that multiple environment variables can be overridden simultaneously."""
        # Clear existing MCP_ vars and set multiple vars
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_SERVER_NAME"] = "Test Server"
        env_vars["MCP_LOG_LEVEL"] = "WARNING"
        env_vars["MCP_ENABLE_BETA_TOOLS"] = "false"
        env_vars["MCP_DEFAULT_PAGE_SIZE"] = "10"
        env_vars["MCP_MAX_PAGE_SIZE"] = "50"

        with patch.dict(os.environ, env_vars, clear=True):
            config = MCPServerConfig()

            assert config.server_name == "Test Server"
            assert config.log_level == "WARNING"
            assert config.enable_beta_tools is False
            assert config.default_page_size == 10
            assert config.max_page_size == 50
