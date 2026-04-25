from enum import Enum
from typing import Protocol, TypeAlias

from deps_agentic_ai.domain.model.conversation import ConversationInfo

from ..shared import Pagination
from .completion import CompletionInfo

__all__ = [
    "IQueryConversationRepository",
    "ConversationSortField",
    "ConversationSortOrder",
    "GroupedConversationsResult",
]


GroupedConversationsResult: TypeAlias = tuple[dict[str, list[ConversationInfo]], int]


class ConversationSortField(str, Enum):
    TITLE = "title"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    AGENT_VENDOR_ID = "agent_vendor_id"


class ConversationSortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class IQueryConversationRepository(Protocol):
    async def conversation_completions(
        self, conversation_id: str, pagination: Pagination | None = None
    ) -> tuple[list[CompletionInfo], int]:
        pass

    async def conversation_exists(self, id_: str, user_id: str, tenant_id: str) -> bool:
        pass

    async def find_all(
        self,
        tenant_id: str,
        created_by: str,
        page: int,
        size: int,
        mode: str | None = None,
        title: str | None = None,
        agent_vendor_id: str | None = None,
        document_ids: list[str] | None = None,
        sort_by: ConversationSortField = ConversationSortField.CREATED_AT,
        sort_order: ConversationSortOrder = ConversationSortOrder.DESC,
    ) -> GroupedConversationsResult:
        pass
