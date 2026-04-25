from typing import Any, Mapping

from deps_agentic_ai.domain.model.tool_set import ParameterData, ToolData, ToolSetData

__all__ = ["ToolSetDataMapper", "ToolSetsDataMapper"]


class ToolSetsDataMapper:
    @staticmethod
    def from_mappings(tool_sets: list[Mapping[str, Any]]) -> list[ToolSetData]:
        return [ToolSetDataMapper.from_mapping(r) for r in tool_sets]


class ToolSetDataMapper:
    @staticmethod
    def from_mapping(tool_set: Mapping[str, Any]) -> ToolSetData:
        return ToolSetData(
            id=tool_set["tool_set_id"],
            code=tool_set["code"],
            name=tool_set["name"],
            tools=[ToolDataMapper.from_mapping(t) for t in tool_set["tools"]],
        )


class ToolDataMapper:
    @staticmethod
    def from_mapping(tool: Mapping[str, Any]) -> ToolData:
        return ToolData(
            code=tool["code"],
            name=tool["name"],
            parameters=[ParameterDataMapper.from_mapping(p) for p in tool["parameters"]],
        )


class ParameterDataMapper:
    @staticmethod
    def from_mapping(parameter: Mapping[str, Any]) -> ParameterData:
        return ParameterData(
            name=parameter["name"],
        )
