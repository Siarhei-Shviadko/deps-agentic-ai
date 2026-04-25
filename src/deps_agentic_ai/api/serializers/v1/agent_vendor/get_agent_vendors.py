from pydantic import Field

from deps_agentic_ai.domain.model.agent_vendor import (
    AgentVendorInfo,
    AgentVendorsInfo,
    ConnectionParametersInfo,
)

from ...configured_base_serializer import ConfiguredResponseSerializer

__all__ = ["GetAgentVendorsResponse"]


class ConnectionParametersSerializer(ConfiguredResponseSerializer):
    base_url: str = Field(..., alias="baseUrl")

    @classmethod
    def from_domain(cls, connection_parameters: ConnectionParametersInfo) -> "ConnectionParametersSerializer":
        return cls(base_url=connection_parameters["base_url"])


class AgentVendorSerializer(ConfiguredResponseSerializer):
    id: str
    name: str
    description: str
    active: bool
    avatar_url: str | None = Field(..., alias="avatarUrl")
    connection_parameters: ConnectionParametersSerializer = Field(..., alias="connectionParameters")

    @classmethod
    def from_domain(cls, agent_vendor: AgentVendorInfo) -> "AgentVendorSerializer":
        return cls(
            id=agent_vendor["id"],
            name=agent_vendor["name"],
            description=agent_vendor["description"],
            active=agent_vendor["active"],
            avatar_url=agent_vendor["avatar_url"],
            connection_parameters=ConnectionParametersSerializer.from_domain(agent_vendor["connection_parameters"]),
        )


class GetAgentVendorsResponse(ConfiguredResponseSerializer):
    agent_vendors: list[AgentVendorSerializer] = Field(default_factory=list, alias="agentVendors")

    @classmethod
    def from_domain(cls, agent_vendors: AgentVendorsInfo) -> "GetAgentVendorsResponse":
        return cls(
            agent_vendors=[
                AgentVendorSerializer.from_domain(agent_vendor) for agent_vendor in agent_vendors["agent_vendors"]
            ],
        )
