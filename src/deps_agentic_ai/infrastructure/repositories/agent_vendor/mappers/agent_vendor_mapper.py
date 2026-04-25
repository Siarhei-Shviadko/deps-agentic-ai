from typing import Any, Mapping

from deps_agentic_ai.domain.model.agent_vendor import AgentVendor, ConnectionParameters

__all__ = ["AgentVendorMapper"]


class AgentVendorMapper:
    @staticmethod
    def from_mapping(agent_vendor: Mapping[str, Any]) -> AgentVendor:
        return AgentVendor(
            id_=agent_vendor["id"],
            name=agent_vendor["name"],
            description=agent_vendor["description"],
            connection_parameters=ConnectionParameters(basse_url=agent_vendor["connection_parameters"]["base_url"]),
            active=agent_vendor["active"],
            avatar_url=agent_vendor["avatar_url"],
        )

    @staticmethod
    def to_dict(agent_vendor: AgentVendor) -> dict[str, Any]:
        return {
            "id": agent_vendor.id(),
            "name": agent_vendor.name,
            "description": agent_vendor.description,
            "connection_parameters": {"base_url": agent_vendor.connection_parameters.base_url},
            "active": agent_vendor.active,
            "avatar_url": agent_vendor.avatar_url,
        }
