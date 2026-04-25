from pydantic import Field

from deps_agentic_ai.domain.model.mode import (
    ModeInfo,
    ModesInfo,
    ParameterInfo,
    ToolInfo,
    ToolSetInfo,
)

from ...configured_base_serializer import ConfiguredResponseSerializer

__all__ = ["GetModesResponse"]


class ParameterSerializer(ConfiguredResponseSerializer):
    name: str

    @classmethod
    def from_domain(cls, parameter: ParameterInfo) -> "ParameterSerializer":
        return cls(name=parameter["name"])


class ToolSerializer(ConfiguredResponseSerializer):
    code: str
    name: str
    parameters: list[ParameterSerializer]

    @classmethod
    def from_domain(cls, tool: ToolInfo) -> "ToolSerializer":
        return cls(
            code=tool["code"],
            name=tool["name"],
            parameters=[ParameterSerializer.from_domain(p) for p in tool["parameters"]],
        )


class ToolSetSerializer(ConfiguredResponseSerializer):
    id: str
    code: str
    name: str
    tools: list[ToolSerializer]

    @classmethod
    def from_domain(cls, tool_set: ToolSetInfo) -> "ToolSetSerializer":
        return cls(
            id=tool_set["id"],
            code=tool_set["code"],
            name=tool_set["name"],
            tools=[ToolSerializer.from_domain(t) for t in tool_set["tools"]],
        )


class ModeSerializer(ConfiguredResponseSerializer):
    id: str
    code: str
    tool_sets: list[ToolSetSerializer] = Field(..., alias="toolSets")

    @classmethod
    def from_domain(cls, mode: ModeInfo) -> "ModeSerializer":
        return cls(
            id=mode["id"],
            code=mode["code"],
            tool_sets=[ToolSetSerializer.from_domain(ts) for ts in mode["tool_sets"]],
        )


class GetModesResponse(ConfiguredResponseSerializer):
    modes: list[ModeSerializer]

    @classmethod
    def from_domain(cls, modes: ModesInfo) -> "GetModesResponse":
        return cls(
            modes=[ModeSerializer.from_domain(m) for m in modes["modes"]],
        )
