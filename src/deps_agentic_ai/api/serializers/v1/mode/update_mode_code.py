from pydantic import Field

from deps_agentic_ai.domain.model.mode import MIN_MODE_CODE_LENGTH

from ...configured_base_serializer import ConfiguredRequestSerializer

__all__ = ["UpdateModeCodeRequest"]


class UpdateModeCodeRequest(ConfiguredRequestSerializer):
    code: str = Field(..., min_length=MIN_MODE_CODE_LENGTH)
