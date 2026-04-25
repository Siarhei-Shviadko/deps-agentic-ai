import json
from typing import Any, Mapping

from deps_agentic_ai.domain.model.agent_vendor import AgentVendorId
from deps_agentic_ai.domain.model.conversation import Conversation, Relation
from deps_agentic_ai.domain.model.shared import EntityId, TenantId, UserId

from .completion import CompletionMapper
from .context import ContextMapper
from .mode import ModeMapper

__all__ = ["ConversationMapper"]


class ConversationMapper:
    @staticmethod
    def from_mapping(conversation: Mapping[str, Any]) -> Conversation:
        mode_data = {
            "id": conversation["mode_id"],
            "code": conversation["mode_code"],
            "created_at": conversation["mode_created_at"],
            "tool_sets": conversation["tool_sets"],
        }
        mode = ModeMapper.from_mapping(mode_data)

        context = ContextMapper.from_mapping(conversation["context"])

        return Conversation(
            id_=EntityId(conversation["id"]),
            tenant_id=TenantId(conversation["tenant_id"]),
            agent_vendor_id=AgentVendorId(conversation["agent_vendor_id"]),
            mode=mode,
            context=context,
            relation=Relation(details=json.loads(conversation["relation"]))
            if conversation["relation"] is not None
            else None,
            title=conversation["title"],
            completions=[
                CompletionMapper.from_mapping(completion_data) for completion_data in conversation["completions"]
            ],
            created_by=UserId(conversation["created_by"]),
            created_at=conversation["created_at"],
            updated_at=conversation["updated_at"],
        )

    @staticmethod
    def to_dict(conversation: Conversation) -> dict[str, Any]:
        return {
            "id": conversation.id(),
            "tenant_id": conversation.tenant_id(),
            "agent_vendor_id": conversation.agent_vendor_id(),
            "mode_id": conversation.mode.id,
            "context": ContextMapper.to_dict(conversation.context),
            "relation": json.dumps(conversation.relation.details) if conversation.relation else None,
            "title": conversation.title,
            "created_by": conversation.created_by,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
        }
