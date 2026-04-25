from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from deps_agentic_ai.domain.model.conversation import (
    Conversation,
    ICommandConversationRepository,
)

from ..tables import conversation_table
from .completion_repository import CompletionRepository
from .conversation_query_factory import ConversationQueryFactory
from .mappers import ConversationMapper

__all__ = ["UoWCommandConversationRepository"]


class UoWCommandConversationRepository(ICommandConversationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._completion_repository = CompletionRepository(session)
        self._query_factory = ConversationQueryFactory()

    async def save(self, conversation: Conversation) -> None:
        query = self._query_factory.save_query().values(**ConversationMapper.to_dict(conversation))

        await self._session.execute(query)

        if completions := conversation.completions:
            await self._completion_repository.save_all(conversation.id(), completions)

    async def conversation_of_id(
        self,
        id_: str,
        user_id: str,
        tenant_id: str,
    ) -> Conversation | None:
        query = self._query_factory.find_by_id_query(id_=id_, user_id=user_id, tenant_id=tenant_id)

        rows = await self._session.execute(query)
        result = rows.mappings().first()

        if not result:
            return None

        return ConversationMapper.from_mapping(dict(result))

    async def conversation_exists(self, id_: str, user_id: str, tenant_id: str) -> bool:
        rows = await self._session.execute(
            self._query_factory.conversation_exists_query(
                id_=id_,
                user_id=user_id,
                tenant_id=tenant_id,
            )
        )

        return bool(rows.mappings().first())

    async def conversations_of_ids(self, ids: list[str], user_id: str, tenant_id: str) -> list[Conversation]:
        query = self._query_factory.find_by_ids_query(ids=ids, user_id=user_id, tenant_id=tenant_id)

        rows = await self._session.execute(query)
        result = rows.mappings()

        return [ConversationMapper.from_mapping(dict(row)) for row in result]

    async def conversations_with_mode(self, mode_id: str) -> list[Conversation]:
        query = self._query_factory.find_by_mode_id_query(mode_id)

        rows = await self._session.execute(query)
        result = rows.mappings()

        return [ConversationMapper.from_mapping(dict(row)) for row in result]

    async def conversations_with_modes(self, mode_ids: list[str]) -> list[Conversation]:
        query = self._query_factory.find_by_mode_ids_query(mode_ids)

        rows = await self._session.execute(query)
        result = rows.mappings()

        return [ConversationMapper.from_mapping(dict(row)) for row in result]

    async def conversations_with_agent_vendor(self, agent_vendor_id: str) -> list[Conversation]:
        query = self._query_factory.find_by_agent_vendor_id_query(agent_vendor_id=agent_vendor_id)

        rows = await self._session.execute(query)
        result = rows.mappings()

        return [ConversationMapper.from_mapping(dict(row)) for row in result]

    async def conversations_with_document_relation(self, document_id: str) -> list[Conversation]:
        query = self._query_factory.find_by_document_relation_query(document_id=document_id)

        rows = await self._session.execute(query)
        result = rows.mappings()

        return [ConversationMapper.from_mapping(dict(row)) for row in result]

    async def conversations_with_document_type_relation(
        self, document_type_id: str, tenant_id: str
    ) -> list[Conversation]:
        query = self._query_factory.find_by_document_type_relation_query(
            document_type_id=document_type_id, tenant_id=tenant_id
        )

        rows = await self._session.execute(query)
        result = rows.mappings()

        return [ConversationMapper.from_mapping(dict(row)) for row in result]

    async def delete_all(self, conversations: list[Conversation]) -> None:
        if conversations:
            await self._session.execute(
                self._query_factory.delete_all_query([conversation.id() for conversation in conversations])
            )

    async def _erase_all(self) -> None:
        query = delete(conversation_table)

        await self._session.execute(query)

    async def update(self, conversation: Conversation) -> None:
        query = self._query_factory.save_query().values(**ConversationMapper.to_dict(conversation))

        await self._session.execute(query)

        await self._completion_repository.delete_all(conversation.id())

        if completions := conversation.completions:
            await self._completion_repository.save_all(conversation.id(), completions)
