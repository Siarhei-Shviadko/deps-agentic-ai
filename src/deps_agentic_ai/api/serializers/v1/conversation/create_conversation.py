from typing import TypeAlias

from pydantic import Field

from deps_agentic_ai.domain.model.conversation import ArgumentData, Conversation
from deps_agentic_ai.domain.model.shared import ToolCode, ToolSetCode

from ...configured_base_serializer import (
    ConfiguredRequestSerializer,
    ConfiguredResponseSerializer,
)

__all__ = ["CreateConversationRequest", "ShortConversationResponse"]

ContextArguments: TypeAlias = dict[ToolSetCode, dict[ToolCode, list["ArgumentDataSerializer"]]]


class ArgumentDataSerializer(ConfiguredRequestSerializer):
    parameter: str
    value: str

    def to_data(self) -> ArgumentData:
        return ArgumentData(parameter=self.parameter, value=self.value)


class CreateConversationRequest(ConfiguredRequestSerializer):
    agent_vendor_id: str = Field(..., alias="agentVendorId")
    mode_id: str = Field(..., alias="modeId")
    title: str
    arguments: ContextArguments
    relation: dict[str, str] | None = None


class ShortConversationResponse(ConfiguredResponseSerializer):
    id: str

    @classmethod
    def from_domain(cls, conversation: Conversation) -> "ShortConversationResponse":
        return cls(
            id=conversation.id(),
        )
