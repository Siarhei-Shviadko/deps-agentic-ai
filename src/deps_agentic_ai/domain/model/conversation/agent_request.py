from dataclasses import dataclass
from typing import Any

from .mode import ContextData

__all__ = ["AgentRequest"]


@dataclass
class AgentRequest:
    conversation_id: str
    question: str
    completion_id: str
    agent_vendor_base_url: str
    context: ContextData
    active_tool_sets: set[str]
    context_bundle: dict[str, Any]
