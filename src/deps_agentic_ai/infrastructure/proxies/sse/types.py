from dataclasses import dataclass
from enum import Enum

__all__ = ["SSEEvent", "SSEEventType"]


class SSEEventType(str, Enum):
    TOOL_CALL = "ToolCall"
    REASONING = "Reasoning"
    TOOL_CALL_RESPONSE = "ToolCallResponse"
    FINAL = "Final"

    @classmethod
    def from_string(cls, value: str) -> "SSEEventType | None":
        try:
            for event_type in cls:
                if event_type.value == value:
                    return event_type
            return None
        except (ValueError, AttributeError):
            return None


@dataclass(frozen=True)
class SSEEvent:
    type: SSEEventType
    text: str

    def __post_init__(self) -> None:
        if not isinstance(self.type, SSEEventType):
            raise ValueError(f"Invalid event type: {self.type}")
        if not isinstance(self.text, str):
            raise ValueError(f"Event text must be a string, got {type(self.text)}")
