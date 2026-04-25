from pydantic import Field

from ...configured_base_serializer import ConfiguredRequestSerializer

__all__ = ["UpdateModeToolSetsRequest"]


class UpdateModeToolSetsRequest(ConfiguredRequestSerializer):
    tool_sets_to_add_ids: list[str] = Field(..., alias="addIds")
    tool_sets_to_remove_ids: list[str] = Field(..., alias="removeIds")
