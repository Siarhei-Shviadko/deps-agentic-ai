from pydantic import Field

from deps_agentic_ai.domain.model.tool_set import (
    MIN_PARAMETER_NAME_LENGTH,
    MIN_TOOL_CODE_LENGTH,
    MIN_TOOL_NAME_LENGTH,
    MIN_TOOL_PARAMETERS_COUNT,
    MIN_TOOL_SET_CODE_LENGTH,
    MIN_TOOL_SET_NAME_LENGTH,
    MIN_TOOL_SET_TOOLS_COUNT,
    ParameterData,
    ToolData,
    ToolSet,
)

from ...configured_base_serializer import (
    ConfiguredRequestSerializer,
    ConfiguredResponseSerializer,
)

__all__ = ["RegisterToolSetRequest", "RegisterToolSetResponse"]


class ParameterSerializer(ConfiguredRequestSerializer):
    name: str = Field(..., min_length=MIN_PARAMETER_NAME_LENGTH)

    def to_domain(self) -> ParameterData:
        return ParameterData(name=self.name)


class ToolSerializer(ConfiguredRequestSerializer):
    code: str = Field(..., min_length=MIN_TOOL_CODE_LENGTH)
    name: str = Field(..., min_length=MIN_TOOL_NAME_LENGTH)
    parameters: list[ParameterSerializer] = Field(..., min_items=MIN_TOOL_PARAMETERS_COUNT)

    def to_domain(self) -> ToolData:
        return ToolData(code=self.code, name=self.name, parameters=[p.to_domain() for p in self.parameters])


class RegisterToolSetRequest(ConfiguredRequestSerializer):
    code: str = Field(..., min_length=MIN_TOOL_SET_CODE_LENGTH)
    name: str = Field(..., min_length=MIN_TOOL_SET_NAME_LENGTH)
    tools: list[ToolSerializer] = Field(..., min_items=MIN_TOOL_SET_TOOLS_COUNT)


class RegisterToolSetResponse(ConfiguredResponseSerializer):
    id: str

    @classmethod
    def from_domain(cls, tool_set: ToolSet) -> "RegisterToolSetResponse":
        return cls(
            id=tool_set.id(),
        )
