from typing import Any, Mapping

from deps_agentic_ai.domain.model.tool_set import Parameter, Tool, ToolSet

__all__ = ["ToolSetMapper", "ToolSetsMapper"]


class ToolSetsMapper:
    @staticmethod
    def from_mappings(tool_sets: list[Mapping[str, Any]]) -> list[ToolSet]:
        return [ToolSetMapper.from_mapping(r) for r in tool_sets]


class ToolSetMapper:
    @staticmethod
    def from_mapping(tool_set: Mapping[str, Any]) -> ToolSet:
        return ToolSet(
            id_=tool_set["tool_set_id"],
            code=tool_set["code"],
            name=tool_set["name"],
            tools=[ToolMapper.from_mapping(t) for t in tool_set["tools"]],
            created_at=tool_set["created_at"],
        )

    @staticmethod
    def to_dict(tool_set: ToolSet) -> dict[str, Any]:
        return {
            "tool_set_id": tool_set.id(),
            "code": tool_set.code,
            "name": tool_set.name,
            "tools": [ToolMapper.to_dict(t) for t in tool_set.tools],
            "created_at": tool_set.created_at,
        }


class ToolMapper:
    @staticmethod
    def from_mapping(tool: Mapping[str, Any]) -> Tool:
        return Tool(
            code=tool["code"],
            name=tool["name"],
            parameters=[ParameterMapper.from_mapping(p) for p in tool["parameters"]],
        )

    @staticmethod
    def to_dict(tool: Tool) -> dict[str, Any]:
        return {
            "code": tool.code,
            "name": tool.name,
            "parameters": [ParameterMapper.to_dict(p) for p in tool.parameters],
        }


class ParameterMapper:
    @staticmethod
    def from_mapping(parameter: Mapping[str, Any]) -> Parameter:
        return Parameter(
            name=parameter["name"],
        )

    @staticmethod
    def to_dict(parameter: Parameter) -> dict[str, Any]:
        return {
            "name": parameter.name,
        }
