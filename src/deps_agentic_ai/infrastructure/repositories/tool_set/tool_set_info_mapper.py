from typing import Any, Mapping

from deps_agentic_ai.domain.model.tool_set import (
    ParameterInfo,
    ToolInfo,
    ToolSetInfo,
    ToolSetsInfo,
)

__all__ = ["ToolSetsInfoMapper", "ToolSetInfoMapper"]


class ToolSetsInfoMapper:
    @staticmethod
    def from_mappings(tool_sets: list[Mapping[str, Any]]) -> ToolSetsInfo:
        return ToolSetsInfo(tool_sets=[ToolSetInfoMapper.from_mapping(r) for r in tool_sets])


class ToolSetInfoMapper:
    @staticmethod
    def from_mapping(tool_set: Mapping[str, Any]) -> ToolSetInfo:
        return ToolSetInfo(
            id=tool_set["tool_set_id"],
            code=tool_set["code"],
            name=tool_set["name"],
            tools=[ToolInfoMapper.from_mapping(t) for t in tool_set["tools"]],
        )


class ToolInfoMapper:
    @staticmethod
    def from_mapping(tool: Mapping[str, Any]) -> ToolInfo:
        return ToolInfo(
            code=tool["code"],
            name=tool["name"],
            parameters=[ParameterInfoMapper.from_mapping(p) for p in tool["parameters"]],
        )


class ParameterInfoMapper:
    @staticmethod
    def from_mapping(parameter: Mapping[str, Any]) -> ParameterInfo:
        return ParameterInfo(
            name=parameter["name"],
        )
