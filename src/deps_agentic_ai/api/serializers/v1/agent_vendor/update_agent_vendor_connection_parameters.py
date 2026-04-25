from pydantic import Field

from ...configured_base_serializer import ConfiguredRequestSerializer

__all__ = ["UpdateAgentVendorConnectionParametersRequest"]


class UpdateAgentVendorConnectionParametersRequest(ConfiguredRequestSerializer):
    base_url: str = Field(..., alias="baseUrl")
