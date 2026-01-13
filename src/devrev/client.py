"""DevRev SDK Client.

Main client classes for interacting with the DevRev API.
"""

from typing import Self

from devrev.config import DevRevConfig, get_config
from devrev.services.accounts import AccountsService, AsyncAccountsService
from devrev.services.dev_users import AsyncDevUsersService, DevUsersService
from devrev.services.rev_users import AsyncRevUsersService, RevUsersService
from devrev.services.works import AsyncWorksService, WorksService
from devrev.utils.http import AsyncHTTPClient, HTTPClient


class DevRevClient:
    """Synchronous DevRev API client.

    Usage:
        ```python
        from devrev import DevRevClient

        # Initialize with environment variables
        client = DevRevClient()

        # Or with explicit configuration
        client = DevRevClient(api_token="your-token")

        # Access services
        accounts = client.accounts.list()
        works = client.works.get("work:123")
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

        # Initialize HTTP client
        self._http = HTTPClient(
            base_url=self._config.base_url,
            api_token=self._config.api_token,
            timeout=self._config.timeout,
            max_retries=self._config.max_retries,
        )

        # Initialize services
        self._accounts = AccountsService(self._http)
        self._works = WorksService(self._http)
        self._dev_users = DevUsersService(self._http)
        self._rev_users = RevUsersService(self._http)

    @property
    def accounts(self) -> AccountsService:
        """Access the Accounts service."""
        return self._accounts

    @property
    def works(self) -> WorksService:
        """Access the Works service."""
        return self._works

    @property
    def dev_users(self) -> DevUsersService:
        """Access the Dev Users service."""
        return self._dev_users

    @property
    def rev_users(self) -> RevUsersService:
        """Access the Rev Users service."""
        return self._rev_users

    def close(self) -> None:
        """Close the client and release resources."""
        self._http.close()

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
                accounts = await client.accounts.list()
                work = await client.works.get("work:123")

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

        # Initialize async HTTP client
        self._http = AsyncHTTPClient(
            base_url=self._config.base_url,
            api_token=self._config.api_token,
            timeout=self._config.timeout,
            max_retries=self._config.max_retries,
        )

        # Initialize async services
        self._accounts = AsyncAccountsService(self._http)
        self._works = AsyncWorksService(self._http)
        self._dev_users = AsyncDevUsersService(self._http)
        self._rev_users = AsyncRevUsersService(self._http)

    @property
    def accounts(self) -> AsyncAccountsService:
        """Access the Accounts service."""
        return self._accounts

    @property
    def works(self) -> AsyncWorksService:
        """Access the Works service."""
        return self._works

    @property
    def dev_users(self) -> AsyncDevUsersService:
        """Access the Dev Users service."""
        return self._dev_users

    @property
    def rev_users(self) -> AsyncRevUsersService:
        """Access the Rev Users service."""
        return self._rev_users

    async def close(self) -> None:
        """Close the client and release resources."""
        await self._http.close()

    async def __aenter__(self) -> Self:
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager."""
        await self.close()
