"""DevRev SDK Client.

Main client classes for interacting with the DevRev API.
"""

from typing import Self

from devrev.config import DevRevConfig, get_config
from devrev.services.accounts import AccountsService, AsyncAccountsService
from devrev.services.articles import ArticlesService, AsyncArticlesService
from devrev.services.code_changes import AsyncCodeChangesService, CodeChangesService
from devrev.services.conversations import (
    AsyncConversationsService,
    ConversationsService,
)
from devrev.services.dev_users import AsyncDevUsersService, DevUsersService
from devrev.services.groups import AsyncGroupsService, GroupsService
from devrev.services.links import AsyncLinksService, LinksService
from devrev.services.parts import AsyncPartsService, PartsService
from devrev.services.rev_users import AsyncRevUsersService, RevUsersService
from devrev.services.slas import AsyncSlasService, SlasService
from devrev.services.tags import AsyncTagsService, TagsService
from devrev.services.timeline_entries import (
    AsyncTimelineEntriesService,
    TimelineEntriesService,
)
from devrev.services.webhooks import AsyncWebhooksService, WebhooksService
from devrev.services.works import AsyncWorksService, WorksService
from devrev.utils.http import (
    AsyncHTTPClient,
    CircuitBreakerConfig,
    ConnectionPoolConfig,
    HTTPClient,
)


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

        # Build pool config from settings
        pool_config = ConnectionPoolConfig(
            max_connections=self._config.max_connections,
            max_keepalive_connections=self._config.max_keepalive_connections,
            keepalive_expiry=self._config.keepalive_expiry,
            http2=self._config.http2,
        )

        # Build circuit breaker config from settings
        circuit_breaker_config = CircuitBreakerConfig(
            failure_threshold=self._config.circuit_breaker_threshold,
            recovery_timeout=self._config.circuit_breaker_recovery_timeout,
            half_open_max_calls=self._config.circuit_breaker_half_open_max_calls,
            enabled=self._config.circuit_breaker_enabled,
        )

        # Initialize HTTP client with all config options
        self._http = HTTPClient(
            base_url=self._config.base_url,
            api_token=self._config.api_token,
            timeout=self._config.timeout,
            max_retries=self._config.max_retries,
            pool_config=pool_config,
            circuit_breaker_config=circuit_breaker_config,
        )

        # Initialize services
        self._accounts = AccountsService(self._http)
        self._articles = ArticlesService(self._http)
        self._code_changes = CodeChangesService(self._http)
        self._conversations = ConversationsService(self._http)
        self._dev_users = DevUsersService(self._http)
        self._groups = GroupsService(self._http)
        self._links = LinksService(self._http)
        self._parts = PartsService(self._http)
        self._rev_users = RevUsersService(self._http)
        self._slas = SlasService(self._http)
        self._tags = TagsService(self._http)
        self._timeline_entries = TimelineEntriesService(self._http)
        self._webhooks = WebhooksService(self._http)
        self._works = WorksService(self._http)

    @property
    def accounts(self) -> AccountsService:
        """Access the Accounts service."""
        return self._accounts

    @property
    def articles(self) -> ArticlesService:
        """Access the Articles service."""
        return self._articles

    @property
    def code_changes(self) -> CodeChangesService:
        """Access the Code Changes service."""
        return self._code_changes

    @property
    def conversations(self) -> ConversationsService:
        """Access the Conversations service."""
        return self._conversations

    @property
    def dev_users(self) -> DevUsersService:
        """Access the Dev Users service."""
        return self._dev_users

    @property
    def groups(self) -> GroupsService:
        """Access the Groups service."""
        return self._groups

    @property
    def links(self) -> LinksService:
        """Access the Links service."""
        return self._links

    @property
    def parts(self) -> PartsService:
        """Access the Parts service."""
        return self._parts

    @property
    def rev_users(self) -> RevUsersService:
        """Access the Rev Users service."""
        return self._rev_users

    @property
    def slas(self) -> SlasService:
        """Access the SLAs service."""
        return self._slas

    @property
    def tags(self) -> TagsService:
        """Access the Tags service."""
        return self._tags

    @property
    def timeline_entries(self) -> TimelineEntriesService:
        """Access the Timeline Entries service."""
        return self._timeline_entries

    @property
    def webhooks(self) -> WebhooksService:
        """Access the Webhooks service."""
        return self._webhooks

    @property
    def works(self) -> WorksService:
        """Access the Works service."""
        return self._works

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

        # Build pool config from settings
        pool_config = ConnectionPoolConfig(
            max_connections=self._config.max_connections,
            max_keepalive_connections=self._config.max_keepalive_connections,
            keepalive_expiry=self._config.keepalive_expiry,
            http2=self._config.http2,
        )

        # Build circuit breaker config from settings
        circuit_breaker_config = CircuitBreakerConfig(
            failure_threshold=self._config.circuit_breaker_threshold,
            recovery_timeout=self._config.circuit_breaker_recovery_timeout,
            half_open_max_calls=self._config.circuit_breaker_half_open_max_calls,
            enabled=self._config.circuit_breaker_enabled,
        )

        # Initialize async HTTP client with all config options
        self._http = AsyncHTTPClient(
            base_url=self._config.base_url,
            api_token=self._config.api_token,
            timeout=self._config.timeout,
            max_retries=self._config.max_retries,
            pool_config=pool_config,
            circuit_breaker_config=circuit_breaker_config,
        )

        # Initialize async services
        self._accounts = AsyncAccountsService(self._http)
        self._articles = AsyncArticlesService(self._http)
        self._code_changes = AsyncCodeChangesService(self._http)
        self._conversations = AsyncConversationsService(self._http)
        self._dev_users = AsyncDevUsersService(self._http)
        self._groups = AsyncGroupsService(self._http)
        self._links = AsyncLinksService(self._http)
        self._parts = AsyncPartsService(self._http)
        self._rev_users = AsyncRevUsersService(self._http)
        self._slas = AsyncSlasService(self._http)
        self._tags = AsyncTagsService(self._http)
        self._timeline_entries = AsyncTimelineEntriesService(self._http)
        self._webhooks = AsyncWebhooksService(self._http)
        self._works = AsyncWorksService(self._http)

    @property
    def accounts(self) -> AsyncAccountsService:
        """Access the Accounts service."""
        return self._accounts

    @property
    def articles(self) -> AsyncArticlesService:
        """Access the Articles service."""
        return self._articles

    @property
    def code_changes(self) -> AsyncCodeChangesService:
        """Access the Code Changes service."""
        return self._code_changes

    @property
    def conversations(self) -> AsyncConversationsService:
        """Access the Conversations service."""
        return self._conversations

    @property
    def dev_users(self) -> AsyncDevUsersService:
        """Access the Dev Users service."""
        return self._dev_users

    @property
    def groups(self) -> AsyncGroupsService:
        """Access the Groups service."""
        return self._groups

    @property
    def links(self) -> AsyncLinksService:
        """Access the Links service."""
        return self._links

    @property
    def parts(self) -> AsyncPartsService:
        """Access the Parts service."""
        return self._parts

    @property
    def rev_users(self) -> AsyncRevUsersService:
        """Access the Rev Users service."""
        return self._rev_users

    @property
    def slas(self) -> AsyncSlasService:
        """Access the SLAs service."""
        return self._slas

    @property
    def tags(self) -> AsyncTagsService:
        """Access the Tags service."""
        return self._tags

    @property
    def timeline_entries(self) -> AsyncTimelineEntriesService:
        """Access the Timeline Entries service."""
        return self._timeline_entries

    @property
    def webhooks(self) -> AsyncWebhooksService:
        """Access the Webhooks service."""
        return self._webhooks

    @property
    def works(self) -> AsyncWorksService:
        """Access the Works service."""
        return self._works

    async def close(self) -> None:
        """Close the client and release resources."""
        await self._http.close()

    async def __aenter__(self) -> Self:
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager."""
        await self.close()
