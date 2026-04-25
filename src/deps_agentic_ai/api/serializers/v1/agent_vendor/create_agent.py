from pydantic import Field

from deps_agentic_ai.domain.model.agent_vendor import MIN_NAME_LENGTH, AgentVendor

from ...configured_base_serializer import (
    ConfiguredRequestSerializer,
    ConfiguredResponseSerializer,
)

__all__ = ["CreateAgentVendorRequest", "CreateAgentVendorResponse"]


class CreateAgentVendorRequest(ConfiguredRequestSerializer):
    name: str = Field(..., min_length=MIN_NAME_LENGTH)
    description: str
    base_url: str = Field(..., alias="baseUrl")
    avatar_url: str | None = Field(None, alias="avatarUrl")


class CreateAgentVendorResponse(ConfiguredResponseSerializer):
    id: str

    @classmethod
    def from_domain(cls, agent_vendor: AgentVendor) -> "CreateAgentVendorResponse":
        return cls(
            id=agent_vendor.id(),
        )
