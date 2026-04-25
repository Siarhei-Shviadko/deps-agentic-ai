from pydantic import Field

from deps_agentic_ai.domain.model.agent_vendor import MIN_NAME_LENGTH

from ...configured_base_serializer import ConfiguredRequestSerializer

__all__ = ["UpdateAgentVendorInfoRequest"]


class UpdateAgentVendorInfoRequest(ConfiguredRequestSerializer):
    name: str = Field(..., min_length=MIN_NAME_LENGTH)
    description: str
    avatar_url: str | None = Field(None, alias="avatarUrl")
