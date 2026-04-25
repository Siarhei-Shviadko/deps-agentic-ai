from datetime import datetime
from typing import Any, TypedDict

__all__ = ["RelationInfo", "ConversationInfo", "ConversationModeInfo"]


class RelationInfo(TypedDict):
    details: dict[str, Any]


class ArgumentInfo(TypedDict):
    name: str


class ActiveToolInfo(TypedDict):
    code: str
    arguments: list[ArgumentInfo]


class ConversationModeInfo(TypedDict):
    id: str
    code: str


class ConversationInfo(TypedDict):
    id: str
    agent_vendor_id: str
    mode: ConversationModeInfo
    context: dict[str, list[ActiveToolInfo]]
    relation: RelationInfo | None
    title: str
    created_by: str
    created_at: datetime
    updated_at: datetime
