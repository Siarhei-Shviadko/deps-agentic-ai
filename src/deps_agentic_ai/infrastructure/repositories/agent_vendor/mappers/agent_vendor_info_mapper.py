from typing import Any, Mapping

from deps_agentic_ai.domain.model.agent_vendor import AgentVendorInfo, AgentVendorsInfo

from .connection_parameters_info_mapper import ConnectionParametersInfoMapper

__all__ = ["AgentVendorsInfoMapper"]


class AgentVendorInfoMapper:
    @staticmethod
    def from_mappings(agent_vendor: Mapping[str, Any]) -> AgentVendorInfo:
        return AgentVendorInfo(
            id=agent_vendor["id"],
            name=agent_vendor["name"],
            description=agent_vendor["description"],
            active=agent_vendor["active"],
            avatar_url=agent_vendor["avatar_url"],
            connection_parameters=ConnectionParametersInfoMapper.from_mappings(agent_vendor["connection_parameters"]),
        )


class AgentVendorsInfoMapper:
    @staticmethod
    def from_mappings(agent_vendors: list[Mapping[str, Any]]) -> AgentVendorsInfo:
        return AgentVendorsInfo(
            agent_vendors=[AgentVendorInfoMapper.from_mappings(agent_vendor) for agent_vendor in agent_vendors],
        )
