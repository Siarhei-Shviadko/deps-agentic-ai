import logging

from deps_agentic_ai.domain.exceptions import ConversationNotFound
from deps_agentic_ai.domain.model.conversation import (
    CompletionInfo,
    ConversationSortField,
    ConversationSortOrder,
    GroupedConversationsResult,
    IQueryConversationRepository,
)
from deps_agentic_ai.domain.model.shared import (
    PaginatedResultMetadataInfo,
    Pagination,
    ResultSetInfo,
)

__all__ = ["QueryConversationService"]


class QueryConversationService:
    def __init__(
        self,
        query_conversation_repository: IQueryConversationRepository,
    ) -> None:
        self._query_conversation_repository = query_conversation_repository

        self._logger = logging.getLogger(self.__class__.__name__)

    async def get_conversation_completions(
        self,
        conversation_id: str,
        user_id: str,
        tenant_id: str,
        page: int,
        per_page: int,
    ) -> tuple[list[CompletionInfo], PaginatedResultMetadataInfo]:
        pagination = Pagination(limit=per_page, offset=per_page * page)

        if await self._query_conversation_repository.conversation_exists(
            id_=conversation_id, user_id=user_id, tenant_id=tenant_id
        ):
            completions, total = await self._query_conversation_repository.conversation_completions(
                conversation_id=conversation_id, pagination=pagination
            )

            return completions, PaginatedResultMetadataInfo(
                result_set=ResultSetInfo(
                    count=len(completions), limit=pagination.limit, offset=pagination.offset, total=total
                )
            )

        raise ConversationNotFound(conversation_id)

    async def find_all(
        self,
        tenant_id: str,
        created_by: str,
        page: int,
        size: int,
        sort_by: ConversationSortField,
        sort_order: ConversationSortOrder,
        mode: str | None = None,
        title: str | None = None,
        agent_vendor_id: str | None = None,
        document_ids: list[str] | None = None,
    ) -> GroupedConversationsResult:
        return await self._query_conversation_repository.find_all(
            tenant_id=tenant_id,
            page=page,
            size=size,
            mode=mode,
            title=title,
            agent_vendor_id=agent_vendor_id,
            document_ids=document_ids,
            created_by=created_by,
            sort_by=sort_by,
            sort_order=sort_order,
        )
