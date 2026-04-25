from dataclasses import dataclass
from enum import Enum

__all__ = ["AgentResponse", "AgentResponseType"]


class AgentResponseType(str, Enum):
    TOOL_CALL = "ToolCall"
    REASONING = "Reasoning"
    TOOL_CALL_RESPONSE = "ToolCallResponse"
    FINAL = "Final"


@dataclass
class AgentResponse:
    type: AgentResponseType
    text: str

    def is_execution_context(self) -> bool:
        return self.type in {
            AgentResponseType.TOOL_CALL,
            AgentResponseType.REASONING,
            AgentResponseType.TOOL_CALL_RESPONSE,
        }

    def is_answer(self) -> bool:
        return self.type == AgentResponseType.FINAL
