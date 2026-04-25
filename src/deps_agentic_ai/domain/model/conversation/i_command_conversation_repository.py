from abc import ABC, abstractmethod

from .conversation import Conversation

__all__ = ["ICommandConversationRepository"]


class ICommandConversationRepository(ABC):
    @abstractmethod
    async def save(self, conversation: Conversation) -> None:
        ...

    @abstractmethod
    async def conversation_of_id(self, id_: str, user_id: str, tenant_id: str) -> Conversation | None:
        ...

    @abstractmethod
    async def conversations_of_ids(self, ids: list[str], user_id: str, tenant_id: str) -> list[Conversation]:
        ...

    @abstractmethod
    async def conversations_with_mode(self, mode_id: str) -> list[Conversation]:
        ...

    @abstractmethod
    async def conversations_with_modes(self, mode_ids: list[str]) -> list[Conversation]:
        ...

    @abstractmethod
    async def conversations_with_agent_vendor(self, agent_vendor_id: str) -> list[Conversation]:
        ...

    @abstractmethod
    async def conversations_with_document_relation(self, document_id: str) -> list[Conversation]:
        ...

    @abstractmethod
    async def conversations_with_document_type_relation(
        self, document_type_id: str, tenant_id: str
    ) -> list[Conversation]:
        ...

    @abstractmethod
    async def delete_all(self, conversations: list[Conversation]) -> None:
        ...

    @abstractmethod
    async def update(self, conversation: Conversation) -> None:
        ...
