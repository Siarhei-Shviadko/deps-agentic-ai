from datetime import datetime
from typing import Any

from pydantic import Field

__all__ = [
    "GetConversationsQuery",
    "GetConversationsResponse",
]

from deps_agentic_ai.domain.model.conversation import (
    ConversationInfo,
    ConversationModeInfo,
    ConversationSortField,
    ConversationSortOrder,
    RelationInfo,
)
from deps_agentic_ai.domain.model.conversation.conversation_info import (
    ActiveToolInfo,
    ArgumentInfo,
)

from ...configured_base_serializer import ConfiguredResponseSerializer


class GetConversationsQuery(ConfiguredResponseSerializer):
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Items per page")
    mode: str | None = Field(None, min_length=1, description="Filter by mode")
    title: str | None = Field(None, min_length=1, description="Filter by title substring")
    agent_vendor_id: str | None = Field(None, min_length=1, description="Filter by agent vendor id")
    document_id: list[str] | None = Field(None, description="Filter by document IDs", alias="documentId")
    sort_by: ConversationSortField = Field(ConversationSortField.CREATED_AT, description="Sorting field")
    sort_order: ConversationSortOrder = Field(ConversationSortOrder.DESC, description="Sorting order")


class ArgumentSerializer(ConfiguredResponseSerializer):
    name: str

    @classmethod
    def from_domain(cls, argument: ArgumentInfo) -> "ArgumentSerializer":
        return cls(name=argument["name"])


class ActiveToolSerializer(ConfiguredResponseSerializer):
    code: str
    arguments: list[ArgumentSerializer]

    @classmethod
    def from_domain(cls, tool: ActiveToolInfo) -> "ActiveToolSerializer":
        return cls(
            code=tool["code"],
            arguments=[ArgumentSerializer.from_domain(arg) for arg in tool["arguments"]],
        )


class ContextSerializer(ConfiguredResponseSerializer):
    tools: dict[str, list[ActiveToolSerializer]]

    @classmethod
    def from_domain(cls, context: dict[str, list[ActiveToolInfo]]) -> "ContextSerializer":
        tools = {}
        for key, value in context.items():
            tools[key] = [ActiveToolSerializer.from_domain(local_tool) for local_tool in value]

        return cls(tools=tools)


class RelationSerializer(ConfiguredResponseSerializer):
    details: dict[str, Any]

    @classmethod
    def from_domain(cls, relation: RelationInfo) -> "RelationSerializer":
        return cls(details=relation["details"])


class ConversationModeSerializer(ConfiguredResponseSerializer):
    id: str
    code: str

    @classmethod
    def from_domain(cls, conversation_mode: ConversationModeInfo) -> "ConversationModeSerializer":
        return cls(
            id=conversation_mode["id"],
            code=conversation_mode["code"],
        )


class ConversationSerializer(ConfiguredResponseSerializer):
    id: str
    agent_vendor_id: str = Field(..., alias="agentVendorId")
    mode: ConversationModeSerializer
    context: ContextSerializer
    relation: RelationSerializer | None
    title: str
    created_by: str = Field(..., alias="createdBy")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    @classmethod
    def from_domain(cls, conversation: ConversationInfo) -> "ConversationSerializer":
        return cls(
            id=conversation["id"],
            agent_vendor_id=conversation["agent_vendor_id"],
            mode=ConversationModeSerializer.from_domain(conversation["mode"]),
            context=ContextSerializer.from_domain(conversation["context"]),
            relation=(
                RelationSerializer.from_domain(conversation["relation"]) if conversation.get("relation") else None
            ),
            title=conversation["title"],
            created_by=conversation["created_by"],
            created_at=conversation["created_at"],
            updated_at=conversation["updated_at"],
        )


class GetConversationsResponse(ConfiguredResponseSerializer):
    items: dict[str, list[ConversationSerializer]]
    total: int

    @classmethod
    def from_domain(
        cls,
        grouped: dict[str, list[ConversationInfo]],
        total: int,
    ) -> "GetConversationsResponse":
        serialized_items = {
            doc_id: [ConversationSerializer.from_domain(c) for c in convs] for doc_id, convs in grouped.items()
        }
        return cls(items=serialized_items, total=total)
