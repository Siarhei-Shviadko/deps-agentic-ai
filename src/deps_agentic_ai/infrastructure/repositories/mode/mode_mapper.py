from typing import Any, Mapping

from deps_agentic_ai.domain.model.mode import Mode, Parameter, Tool, ToolSet

__all__ = ["ModeMapper", "ModesMapper"]


class ModesMapper:
    @staticmethod
    def from_mappings(modes: list[Mapping[str, Any]]) -> list[Mode]:
        return [ModeMapper.from_mapping(m) for m in modes]


class ModeMapper:
    @staticmethod
    def from_mapping(mode: Mapping[str, Any]) -> Mode:
        return Mode(
            id_=mode["mode_id"],
            code=mode["code"],
            tool_sets=[ToolSetMapper.from_mapping(ts) for ts in mode["tool_sets"]],
            created_at=mode["created_at"],
        )

    @staticmethod
    def to_dict(mode: Mode) -> dict[str, Any]:
        return {
            "mode_id": mode.id(),
            "code": mode.code,
            "tool_set_ids": [ts.id() for ts in mode.tool_sets.values()],
            "created_at": mode.created_at,
        }


class ToolSetMapper:
    @staticmethod
    def from_mapping(tool_set: Mapping[str, Any]) -> ToolSet:
        return ToolSet(
            id_=tool_set["tool_set_id"],
            code=tool_set["code"],
            name=tool_set["name"],
            tools=[ToolMapper.from_mapping(t) for t in tool_set["tools"]],
        )


class ToolMapper:
    @staticmethod
    def from_mapping(tool: Mapping[str, Any]) -> Tool:
        return Tool(
            code=tool["code"],
            name=tool["name"],
            parameters=[ParameterMapper.from_mapping(p) for p in tool["parameters"]],
        )


class ParameterMapper:
    @staticmethod
    def from_mapping(parameter: Mapping[str, Any]) -> Parameter:
        return Parameter(
            name=parameter["name"],
        )
