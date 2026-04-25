import json
from typing import Any, Mapping

from deps_agentic_ai.domain.model.conversation import ConversationInfo
from deps_agentic_ai.domain.model.conversation.conversation_info import (
    ConversationModeInfo,
    RelationInfo,
)

__all__ = ["ConversationInfoMapper"]


class ConversationModeInfoMapper:
    @staticmethod
    def from_mapping(conversation: Mapping[str, Any]) -> ConversationModeInfo:
        return ConversationModeInfo(
            id=conversation["mode_id"],
            code=conversation["mode_code"],
        )


class ConversationInfoMapper:
    @staticmethod
    def from_mapping(conversation: Mapping[str, Any]) -> ConversationInfo:
        return ConversationInfo(
            id=conversation["id"],
            agent_vendor_id=conversation["agent_vendor_id"],
            mode=ConversationModeInfoMapper.from_mapping(conversation),
            context=conversation["context"],
            relation=RelationInfo(details=json.loads(conversation["relation"]))  # type: ignore
            if conversation["relation"] is not None
            else None,
            title=conversation["title"],
            created_by=conversation["created_by"],
            created_at=conversation["created_at"],
            updated_at=conversation["updated_at"],
        )
