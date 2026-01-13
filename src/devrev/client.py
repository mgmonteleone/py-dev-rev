"""DevRev SDK Client.

Main client classes for interacting with the DevRev API.
This module will be fully implemented in Phase 2.
"""

from typing import Self

from devrev.config import DevRevConfig, get_config


class DevRevClient:
    """Synchronous DevRev API client.

    Usage:
        ```python
        from devrev import DevRevClient

        # Initialize with environment variables
        client = DevRevClient()

        # Or with explicit configuration
        client = DevRevClient(api_token="your-token")
        ```
    """

    def __init__(
        self,
        *,
        api_token: str | None = None,
        base_url: str | None = None,
        timeout: int | None = None,
        config: DevRevConfig | None = None,
    ) -> None:
        """Initialize the DevRev client.

        Args:
            api_token: DevRev API token (or set DEVREV_API_TOKEN env var)
            base_url: API base URL (default: https://api.devrev.ai)
            timeout: Request timeout in seconds (default: 30)
            config: Full configuration object (overrides other params)
        """
        if config:
            self._config = config
        else:
            config_kwargs: dict[str, str | int] = {}
            if api_token:
                config_kwargs["api_token"] = api_token
            if base_url:
                config_kwargs["base_url"] = base_url
            if timeout:
                config_kwargs["timeout"] = timeout

            if config_kwargs:
                self._config = DevRevConfig(**config_kwargs)  # type: ignore[arg-type]
            else:
                self._config = get_config()

    def close(self) -> None:
        """Close the client and release resources."""
        # Will be implemented in Phase 2 with HTTP client

    def __enter__(self) -> Self:
        """Enter context manager."""
        return self

    def __exit__(self, *args: object) -> None:
        """Exit context manager."""
        self.close()


class AsyncDevRevClient:
    """Asynchronous DevRev API client.

    Usage:
        ```python
        import asyncio
        from devrev import AsyncDevRevClient

        async def main():
            async with AsyncDevRevClient() as client:
                # Use async client
                pass

        asyncio.run(main())
        ```
    """

    def __init__(
        self,
        *,
        api_token: str | None = None,
        base_url: str | None = None,
        timeout: int | None = None,
        config: DevRevConfig | None = None,
    ) -> None:
        """Initialize the async DevRev client.

        Args:
            api_token: DevRev API token (or set DEVREV_API_TOKEN env var)
            base_url: API base URL (default: https://api.devrev.ai)
            timeout: Request timeout in seconds (default: 30)
            config: Full configuration object (overrides other params)
        """
        if config:
            self._config = config
        else:
            config_kwargs: dict[str, str | int] = {}
            if api_token:
                config_kwargs["api_token"] = api_token
            if base_url:
                config_kwargs["base_url"] = base_url
            if timeout:
                config_kwargs["timeout"] = timeout

            if config_kwargs:
                self._config = DevRevConfig(**config_kwargs)  # type: ignore[arg-type]
            else:
                self._config = get_config()

    async def close(self) -> None:
        """Close the client and release resources."""
        # Will be implemented in Phase 2 with HTTP client

    async def __aenter__(self) -> Self:
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager."""
        await self.close()
