from typing import Any

from deps_agentic_ai.domain.model.conversation import Conversation

from ...configured_base_serializer import ConfiguredResponseSerializer
from .completion import CompletionSerializer

__all__ = ["GetConversationResponse"]


class RelationSerializer(ConfiguredResponseSerializer):
    details: dict[str, Any] | None = None


class GetConversationResponse(ConfiguredResponseSerializer):
    id: str
    title: str
    relation: RelationSerializer
    completions: list[CompletionSerializer]

    @classmethod
    def from_domain(cls, conversation: Conversation) -> "GetConversationResponse":
        return cls(
            id=conversation.id(),
            title=conversation.title,
            relation=RelationSerializer(details=conversation.relation.details if conversation.relation else None),
            completions=[CompletionSerializer.from_domain(completion) for completion in conversation.completions],
        )
