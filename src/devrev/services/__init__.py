"""DevRev SDK Service Classes.

This module contains service classes for interacting with DevRev API endpoints.
"""

from devrev.services.accounts import AccountsService, AsyncAccountsService
from devrev.services.articles import ArticlesService, AsyncArticlesService
from devrev.services.base import AsyncBaseService, BaseService
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

__all__ = [
    # Base
    "BaseService",
    "AsyncBaseService",
    # Accounts
    "AccountsService",
    "AsyncAccountsService",
    # Articles
    "ArticlesService",
    "AsyncArticlesService",
    # Brands
    "BrandsService",
    "AsyncBrandsService",
    # Code Changes
    "CodeChangesService",
    "AsyncCodeChangesService",
    # Conversations
    "ConversationsService",
    "AsyncConversationsService",
    # Dev Users
    "DevUsersService",
    "AsyncDevUsersService",
    # Engagements
    "EngagementsService",
    "AsyncEngagementsService",
    # Groups
    "GroupsService",
    "AsyncGroupsService",
    # Incidents
    "IncidentsService",
    "AsyncIncidentsService",
    # Links
    "LinksService",
    "AsyncLinksService",
    # Notifications
    "NotificationsService",
    "AsyncNotificationsService",
    # Parts
    "PartsService",
    "AsyncPartsService",
    # Preferences
    "PreferencesService",
    "AsyncPreferencesService",
    # Question Answers
    "QuestionAnswersService",
    "AsyncQuestionAnswersService",
    # Recommendations
    "RecommendationsService",
    "AsyncRecommendationsService",
    # Rev Users
    "RevUsersService",
    "AsyncRevUsersService",
    # Search
    "SearchService",
    "AsyncSearchService",
    # SLAs
    "SlasService",
    "AsyncSlasService",
    # Tags
    "TagsService",
    "AsyncTagsService",
    # Timeline Entries
    "TimelineEntriesService",
    "AsyncTimelineEntriesService",
    # Track Events
    "TrackEventsService",
    "AsyncTrackEventsService",
    # UOMs
    "UomsService",
    "AsyncUomsService",
    # Webhooks
    "WebhooksService",
    "AsyncWebhooksService",
    # Works
    "WorksService",
    "AsyncWorksService",
]
