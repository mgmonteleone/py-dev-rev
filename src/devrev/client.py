"""DevRev SDK Client.

Main client classes for interacting with the DevRev API.
"""

from typing import Self

from devrev.config import APIVersion, DevRevConfig, get_config
from devrev.exceptions import BetaAPIRequiredError
from devrev.services.accounts import AccountsService, AsyncAccountsService
from devrev.services.articles import ArticlesService, AsyncArticlesService
from devrev.services.artifacts import ArtifactsService, AsyncArtifactsService
from devrev.services.brands import AsyncBrandsService, BrandsService
from devrev.services.code_changes import AsyncCodeChangesService, CodeChangesService
from devrev.services.conversations import (
    AsyncConversationsService,
    ConversationsService,
)
from devrev.services.dev_users import AsyncDevUsersService, DevUsersService
from devrev.services.engagements import (
    AsyncEngagementsService,
    EngagementsService,
)
from devrev.services.groups import AsyncGroupsService, GroupsService
from devrev.services.incidents import AsyncIncidentsService, IncidentsService
from devrev.services.links import AsyncLinksService, LinksService
from devrev.services.notifications import (
    AsyncNotificationsService,
    NotificationsService,
)
from devrev.services.parts import AsyncPartsService, PartsService
from devrev.services.preferences import AsyncPreferencesService, PreferencesService
from devrev.services.question_answers import (
    AsyncQuestionAnswersService,
    QuestionAnswersService,
)
from devrev.services.recommendations import (
    AsyncRecommendationsService,
    RecommendationsService,
)
from devrev.services.rev_users import AsyncRevUsersService, RevUsersService
from devrev.services.search import AsyncSearchService, SearchService
from devrev.services.slas import AsyncSlasService, SlasService
from devrev.services.tags import AsyncTagsService, TagsService
from devrev.services.timeline_entries import (
    AsyncTimelineEntriesService,
    TimelineEntriesService,
)
from devrev.services.track_events import (
    AsyncTrackEventsService,
    TrackEventsService,
)
from devrev.services.uoms import AsyncUomsService, UomsService
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
        api_version: APIVersion | None = None,
        config: DevRevConfig | None = None,
    ) -> None:
        """Initialize the DevRev client.

        Args:
            api_token: DevRev API token (or set DEVREV_API_TOKEN env var)
            base_url: API base URL (default: https://api.devrev.ai)
            timeout: Request timeout in seconds (default: 30)
            api_version: API version to use (default: APIVersion.PUBLIC)
            config: Full configuration object (overrides other params)
        """
        if config:
            self._config = config
        else:
            config_kwargs: dict[str, str | int | APIVersion] = {}
            if api_token:
                config_kwargs["api_token"] = api_token
            if base_url:
                config_kwargs["base_url"] = base_url
            if timeout:
                config_kwargs["timeout"] = timeout
            if api_version:
                config_kwargs["api_version"] = api_version

            if config_kwargs:
                self._config = DevRevConfig(**config_kwargs)  # type: ignore[arg-type]
            else:
                self._config = get_config()

        # Store API version:
        # - When config object is explicitly provided, use config's api_version (config overrides all)
        # - Otherwise, prefer explicit api_version param over the config's default value
        if config:
            self._api_version = self._config.api_version
        else:
            self._api_version = api_version or self._config.api_version

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
        self._articles = ArticlesService(self._http, parent_client=self)
        self._artifacts = ArtifactsService(self._http)
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

        # Beta-only services (initialized but access-guarded)
        self._incidents: IncidentsService | None = None
        self._engagements: EngagementsService | None = None
        self._brands: BrandsService | None = None
        self._uoms: UomsService | None = None
        self._question_answers: QuestionAnswersService | None = None
        self._recommendations: RecommendationsService | None = None
        self._search: SearchService | None = None
        self._preferences: PreferencesService | None = None
        self._notifications: NotificationsService | None = None
        self._track_events: TrackEventsService | None = None

        # Initialize beta services if using beta API
        if self._api_version == APIVersion.BETA:
            self._incidents = IncidentsService(self._http)
            self._engagements = EngagementsService(self._http)
            self._brands = BrandsService(self._http)
            self._uoms = UomsService(self._http)
            self._question_answers = QuestionAnswersService(self._http)
            self._recommendations = RecommendationsService(self._http)
            self._search = SearchService(self._http)
            self._preferences = PreferencesService(self._http)
            self._notifications = NotificationsService(self._http)
            self._track_events = TrackEventsService(self._http)

    @property
    def api_version(self) -> APIVersion:
        """Get the API version being used by this client."""
        return self._api_version

    @property
    def accounts(self) -> AccountsService:
        """Access the Accounts service."""
        return self._accounts

    @property
    def articles(self) -> ArticlesService:
        """Access the Articles service."""
        return self._articles

    @property
    def artifacts(self) -> ArtifactsService:
        """Access the Artifacts service."""
        return self._artifacts

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

    @property
    def incidents(self) -> IncidentsService:
        """Access the Incidents service (beta only)."""
        if self._incidents is None:
            raise BetaAPIRequiredError(
                "The incidents service requires beta API. "
                "Initialize client with api_version=APIVersion.BETA"
            )
        return self._incidents

    @property
    def engagements(self) -> EngagementsService:
        """Access the Engagements service (beta only)."""
        if self._engagements is None:
            raise BetaAPIRequiredError(
                "The engagements service requires beta API. "
                "Initialize client with api_version=APIVersion.BETA"
            )
        return self._engagements

    @property
    def brands(self) -> BrandsService:
        """Access the Brands service (beta only)."""
        if self._brands is None:
            raise BetaAPIRequiredError(
                "The brands service requires beta API. "
                "Initialize client with api_version=APIVersion.BETA"
            )
        return self._brands

    @property
    def uoms(self) -> UomsService:
        """Access the UOMs service (beta only)."""
        if self._uoms is None:
            raise BetaAPIRequiredError(
                "The uoms service requires beta API. "
                "Initialize client with api_version=APIVersion.BETA"
            )
        return self._uoms

    @property
    def question_answers(self) -> QuestionAnswersService:
        """Access the Question Answers service (beta only)."""
        if self._question_answers is None:
            raise BetaAPIRequiredError(
                "The question_answers service requires beta API. "
                "Initialize client with api_version=APIVersion.BETA"
            )
        return self._question_answers

    @property
    def recommendations(self) -> RecommendationsService:
        """Access the Recommendations service (beta only)."""
        if self._recommendations is None:
            raise BetaAPIRequiredError(
                "The recommendations service requires beta API. "
                "Initialize client with api_version=APIVersion.BETA"
            )
        return self._recommendations

    @property
    def search(self) -> SearchService:
        """Access the Search service (beta only)."""
        if self._search is None:
            raise BetaAPIRequiredError(
                "The search service requires beta API. "
                "Initialize client with api_version=APIVersion.BETA"
            )
        return self._search

    @property
    def preferences(self) -> PreferencesService:
        """Access the Preferences service (beta only)."""
        if self._preferences is None:
            raise BetaAPIRequiredError(
                "The preferences service requires beta API. "
                "Initialize client with api_version=APIVersion.BETA"
            )
        return self._preferences

    @property
    def notifications(self) -> NotificationsService:
        """Access the Notifications service (beta only)."""
        if self._notifications is None:
            raise BetaAPIRequiredError(
                "The notifications service requires beta API. "
                "Initialize client with api_version=APIVersion.BETA"
            )
        return self._notifications

    @property
    def track_events(self) -> TrackEventsService:
        """Access the Track Events service (beta only)."""
        if self._track_events is None:
            raise BetaAPIRequiredError(
                "The track_events service requires beta API. "
                "Initialize client with api_version=APIVersion.BETA"
            )
        return self._track_events

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
        api_version: APIVersion | None = None,
        config: DevRevConfig | None = None,
    ) -> None:
        """Initialize the async DevRev client.

        Args:
            api_token: DevRev API token (or set DEVREV_API_TOKEN env var)
            base_url: API base URL (default: https://api.devrev.ai)
            timeout: Request timeout in seconds (default: 30)
            api_version: API version to use (default: APIVersion.PUBLIC)
            config: Full configuration object (overrides other params)
        """
        if config:
            self._config = config
        else:
            config_kwargs: dict[str, str | int | APIVersion] = {}
            if api_token:
                config_kwargs["api_token"] = api_token
            if base_url:
                config_kwargs["base_url"] = base_url
            if timeout:
                config_kwargs["timeout"] = timeout
            if api_version:
                config_kwargs["api_version"] = api_version

            if config_kwargs:
                self._config = DevRevConfig(**config_kwargs)  # type: ignore[arg-type]
            else:
                self._config = get_config()

        # Store API version:
        # - When config object is explicitly provided, use config's api_version (config overrides all)
        # - Otherwise, prefer explicit api_version param over the config's default value
        if config:
            self._api_version = self._config.api_version
        else:
            self._api_version = api_version or self._config.api_version

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
        self._articles = AsyncArticlesService(self._http, parent_client=self)
        self._artifacts = AsyncArtifactsService(self._http)
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

        # Beta-only services (initialized but access-guarded)
        self._incidents: AsyncIncidentsService | None = None
        self._engagements: AsyncEngagementsService | None = None
        self._brands: AsyncBrandsService | None = None
        self._uoms: AsyncUomsService | None = None
        self._question_answers: AsyncQuestionAnswersService | None = None
        self._recommendations: AsyncRecommendationsService | None = None
        self._search: AsyncSearchService | None = None
        self._preferences: AsyncPreferencesService | None = None
        self._notifications: AsyncNotificationsService | None = None
        self._track_events: AsyncTrackEventsService | None = None

        # Initialize beta services if using beta API
        if self._api_version == APIVersion.BETA:
            self._incidents = AsyncIncidentsService(self._http)
            self._engagements = AsyncEngagementsService(self._http)
            self._brands = AsyncBrandsService(self._http)
            self._uoms = AsyncUomsService(self._http)
            self._question_answers = AsyncQuestionAnswersService(self._http)
            self._recommendations = AsyncRecommendationsService(self._http)
            self._search = AsyncSearchService(self._http)
            self._preferences = AsyncPreferencesService(self._http)
            self._notifications = AsyncNotificationsService(self._http)
            self._track_events = AsyncTrackEventsService(self._http)

    @property
    def api_version(self) -> APIVersion:
        """Get the API version being used by this client."""
        return self._api_version

    @property
    def accounts(self) -> AsyncAccountsService:
        """Access the Accounts service."""
        return self._accounts

    @property
    def articles(self) -> AsyncArticlesService:
        """Access the Articles service."""
        return self._articles

    @property
    def artifacts(self) -> AsyncArtifactsService:
        """Access the Artifacts service."""
        return self._artifacts

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

    @property
    def incidents(self) -> AsyncIncidentsService:
        """Access the Incidents service (beta only)."""
        if self._incidents is None:
            raise BetaAPIRequiredError(
                "The incidents service requires beta API. "
                "Initialize client with api_version=APIVersion.BETA"
            )
        return self._incidents

    @property
    def engagements(self) -> AsyncEngagementsService:
        """Access the Engagements service (beta only)."""
        if self._engagements is None:
            raise BetaAPIRequiredError(
                "The engagements service requires beta API. "
                "Initialize client with api_version=APIVersion.BETA"
            )
        return self._engagements

    @property
    def brands(self) -> AsyncBrandsService:
        """Access the Brands service (beta only)."""
        if self._brands is None:
            raise BetaAPIRequiredError(
                "The brands service requires beta API. "
                "Initialize client with api_version=APIVersion.BETA"
            )
        return self._brands

    @property
    def uoms(self) -> AsyncUomsService:
        """Access the UOMs service (beta only)."""
        if self._uoms is None:
            raise BetaAPIRequiredError(
                "The uoms service requires beta API. "
                "Initialize client with api_version=APIVersion.BETA"
            )
        return self._uoms

    @property
    def question_answers(self) -> AsyncQuestionAnswersService:
        """Access the Question Answers service (beta only)."""
        if self._question_answers is None:
            raise BetaAPIRequiredError(
                "The question_answers service requires beta API. "
                "Initialize client with api_version=APIVersion.BETA"
            )
        return self._question_answers

    @property
    def recommendations(self) -> AsyncRecommendationsService:
        """Access the Recommendations service (beta only)."""
        if self._recommendations is None:
            raise BetaAPIRequiredError(
                "The recommendations service requires beta API. "
                "Initialize client with api_version=APIVersion.BETA"
            )
        return self._recommendations

    @property
    def search(self) -> AsyncSearchService:
        """Access the Search service (beta only)."""
        if self._search is None:
            raise BetaAPIRequiredError(
                "The search service requires beta API. "
                "Initialize client with api_version=APIVersion.BETA"
            )
        return self._search

    @property
    def preferences(self) -> AsyncPreferencesService:
        """Access the Preferences service (beta only)."""
        if self._preferences is None:
            raise BetaAPIRequiredError(
                "The preferences service requires beta API. "
                "Initialize client with api_version=APIVersion.BETA"
            )
        return self._preferences

    @property
    def notifications(self) -> AsyncNotificationsService:
        """Access the Notifications service (beta only)."""
        if self._notifications is None:
            raise BetaAPIRequiredError(
                "The notifications service requires beta API. "
                "Initialize client with api_version=APIVersion.BETA"
            )
        return self._notifications

    @property
    def track_events(self) -> AsyncTrackEventsService:
        """Access the Track Events service (beta only)."""
        if self._track_events is None:
            raise BetaAPIRequiredError(
                "The track_events service requires beta API. "
                "Initialize client with api_version=APIVersion.BETA"
            )
        return self._track_events

    async def close(self) -> None:
        """Close the client and release resources."""
        await self._http.close()

    async def __aenter__(self) -> Self:
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager."""
        await self.close()
