from deps_agentic_ai.domain.model.conversation import (
    Conversation,
    ICommandConversationRepository,
)

__all__ = ["FakeCommandConversationRepository"]


class FakeCommandConversationRepository(ICommandConversationRepository):
    def __init__(self, conversations: list[Conversation] | None = None) -> None:
        self._db = {conv.id(): conv for conv in conversations} if conversations else {}

    async def save(self, conversation: Conversation) -> None:
        self._db[conversation.id()] = conversation

    async def conversation_of_id(self, id_: str, user_id: str, tenant_id: str) -> Conversation | None:
        conversation = self._db.get(id_)
        if conversation and conversation.tenant_id.value == tenant_id and conversation.created_by == user_id:
            return conversation
        return None

    async def conversations_of_ids(self, ids: list[str], user_id: str, tenant_id: str) -> list[Conversation]:
        conversations = []
        for id_ in ids:
            conversation = self._db.get(id_)
            if conversation and conversation.created_by == user_id and conversation.tenant_id.value == tenant_id:
                conversations.append(conversation)

        return conversations

    async def conversations_with_mode(self, mode_id: str) -> list[Conversation]:
        return [conversation for conversation in self._db.values() if conversation.mode_id == mode_id]

    async def conversations_with_modes(self, mode_ids: list[str]) -> list[Conversation]:
        return [conversation for conversation in self._db.values() if conversation.mode_id in mode_ids]

    async def conversations_with_agent_vendor(self, agent_vendor_id: str) -> list[Conversation]:
        return [conversation for conversation in self._db.values() if conversation.agent_vendor_id == agent_vendor_id]

    async def conversations_with_document_relation(self, document_id: str) -> list[Conversation]:
        return [
            conversation
            for conversation in self._db.values()
            if (relation := conversation.relation.details.get("documentId") is not None) and relation == document_id
        ]

    async def conversations_with_document_type_relation(
        self, document_type_id: str, tenant_id: str
    ) -> list[Conversation]:
        return [
            conversation
            for conversation in self._db.values()
            if (relation := conversation.relation.details.get("documentTypeId") is not None)
            and relation == document_type_id
            and conversation.tenant.id() == tenant_id
        ]

    async def delete_all(self, conversations: list[Conversation]) -> None:
        for id_ in [conversation.id() for conversation in conversations]:
            del self._db[id_]

    async def conversation_exists(self, id_: str, user_id: str, tenant_id: str) -> bool:
        return bool(await self.conversation_of_id(id_=id_, user_id=user_id, tenant_id=tenant_id))

    async def _erase_all(self) -> None:
        self._db.clear()

    async def update(self, conversation: Conversation) -> None:
        self._db[conversation.id()] = conversation
