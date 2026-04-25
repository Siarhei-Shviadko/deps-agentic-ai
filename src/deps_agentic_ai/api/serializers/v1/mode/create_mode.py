from pydantic import Field

from deps_agentic_ai.domain.model.mode import (
    MIN_MODE_CODE_LENGTH,
    MIN_MODE_TOOL_SETS_COUNT,
    Mode,
)

from ...configured_base_serializer import (
    ConfiguredRequestSerializer,
    ConfiguredResponseSerializer,
)

__all__ = ["CreateModeRequest", "CreateModeResponse"]


class CreateModeRequest(ConfiguredRequestSerializer):
    code: str = Field(..., min_length=MIN_MODE_CODE_LENGTH)
    tool_set_ids: list[str] = Field(..., alias="toolSetIds", min_items=MIN_MODE_TOOL_SETS_COUNT)


class CreateModeResponse(ConfiguredResponseSerializer):
    id: str

    @classmethod
    def from_domain(cls, mode: Mode) -> "CreateModeResponse":
        return cls(
            id=mode.id(),
        )
