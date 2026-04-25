from pydantic import Field

from deps_agentic_ai.domain.model.tool_set import (
    ParameterInfo,
    ToolInfo,
    ToolSetInfo,
    ToolSetsInfo,
)

from ...configured_base_serializer import ConfiguredResponseSerializer

__all__ = ["GetToolSetsResponse"]


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


class GetToolSetsResponse(ConfiguredResponseSerializer):
    tool_sets: list[ToolSetSerializer] = Field(..., alias="toolSets")

    @classmethod
    def from_domain(cls, tool_sets: ToolSetsInfo) -> "GetToolSetsResponse":
        return cls(
            tool_sets=[ToolSetSerializer.from_domain(ts) for ts in tool_sets["tool_sets"]],
        )
