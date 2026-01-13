"""DevRev SDK Service Classes.

This module contains service classes for interacting with DevRev API endpoints.
"""

from devrev.services.accounts import AccountsService, AsyncAccountsService
from devrev.services.articles import ArticlesService, AsyncArticlesService
from devrev.services.base import AsyncBaseService, BaseService
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
    # Code Changes
    "CodeChangesService",
    "AsyncCodeChangesService",
    # Conversations
    "ConversationsService",
    "AsyncConversationsService",
    # Dev Users
    "DevUsersService",
    "AsyncDevUsersService",
    # Groups
    "GroupsService",
    "AsyncGroupsService",
    # Links
    "LinksService",
    "AsyncLinksService",
    # Parts
    "PartsService",
    "AsyncPartsService",
    # Rev Users
    "RevUsersService",
    "AsyncRevUsersService",
    # SLAs
    "SlasService",
    "AsyncSlasService",
    # Tags
    "TagsService",
    "AsyncTagsService",
    # Timeline Entries
    "TimelineEntriesService",
    "AsyncTimelineEntriesService",
    # Webhooks
    "WebhooksService",
    "AsyncWebhooksService",
    # Works
    "WorksService",
    "AsyncWorksService",
]
