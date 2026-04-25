import json
from typing import Any

from fastapi import Query
from pydantic import Field

from deps_agentic_ai.domain.model.conversation import ContextArguments
from deps_agentic_ai.domain.model.conversation.types import ArgumentData
from deps_agentic_ai.infrastructure.proxies import SSEEventType

from ...configured_base_serializer import (
    ConfiguredRequestSerializer,
    ConfiguredResponseSerializer,
)

__all__ = ["ChatRequest", "SSEEventSerializer"]


class ArgumentDataSerializer(ConfiguredRequestSerializer):
    parameter: str
    value: Any

    def to_data(self) -> ArgumentData:
        return ArgumentData(parameter=self.parameter, value=self.value)


class ChatRequest(ConfiguredRequestSerializer):
    user_question: str = Field(..., alias="userQuestion")
    arguments: dict[str, dict[str, list[ArgumentDataSerializer]]] | None = Field(  # noqa: WPS234
        None,
        description="Nested structure: {toolSetCode: {toolCode: [{parameter, value}]}}",
    )

    def to_context_arguments(self) -> ContextArguments | None:
        if self.arguments is None:
            return self.arguments
        return {
            tool_set_code: {tool_code: [arg.to_data() for arg in args] for tool_code, args in tool_args.items()}
            for tool_set_code, tool_args in self.arguments.items()
        }

    @classmethod
    def from_query_params(
        cls,
        user_question: str = Query(..., alias="userQuestion"),
        arguments: str = Query("{}"),
    ) -> "ChatRequest":
        parsed_arguments = json.loads(arguments)
        return cls(userQuestion=user_question, arguments=parsed_arguments)


class SSEEventSerializer(ConfiguredResponseSerializer):
    type: SSEEventType
    text: str
