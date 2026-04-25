from datetime import datetime, timezone
from uuid import uuid4

from ..agent_vendor.agent_vendor_id import AgentVendorId
from ..mode import ModeData
from ..shared import EntityId, TenantId
from ..tool_set import ToolSetData
from .conversation import Conversation
from .mode import ContextArguments, Mode, Parameter, Tool, ToolSet
from .relation import Relation
from .types import RelationData

__all__ = ["ConversationFactory"]


class ConversationFactory:
    @staticmethod
    def create(
        tenant_id: str,
        agent_provider_id: AgentVendorId,
        mode: ModeData,
        relation: RelationData | None,
        arguments: ContextArguments,
        title: str,
        user_id: str,
    ) -> Conversation:
        id_ = uuid4().hex
        now = datetime.now(timezone.utc)

        mode_vo = ConversationFactory._create_mode_vo(mode)

        context = mode_vo.create_context(arguments)

        relation_vo = Relation(details=relation["details"]) if relation else None

        return Conversation(
            id_=EntityId(id_),
            tenant_id=TenantId(tenant_id),
            agent_vendor_id=agent_provider_id,
            mode=mode_vo,
            context=context,
            relation=relation_vo,
            title=title,
            completions=[],
            created_by=user_id,
            created_at=now,
            updated_at=now,
            events=[],
        )

    @staticmethod
    def _create_mode_vo(mode: ModeData) -> Mode:
        return Mode(
            id_=mode["id"],
            code=mode["code"],
            tool_sets=[ConversationFactory._create_tool_set_vo(ts) for ts in mode["tool_sets"]],
        )

    @staticmethod
    def _create_tool_set_vo(tool_set: ToolSetData) -> ToolSet:
        return ToolSet(
            id_=tool_set["id"],
            code=tool_set["code"],
            name=tool_set["name"],
            tools=[
                Tool(code=t["code"], name=t["name"], parameters=[Parameter(name=p["name"]) for p in t["parameters"]])
                for t in tool_set["tools"]
            ],
        )
