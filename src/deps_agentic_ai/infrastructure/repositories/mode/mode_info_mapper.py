from typing import Any, Mapping

from deps_agentic_ai.domain.model.mode import (
    ModeInfo,
    ModesInfo,
    ParameterInfo,
    ToolInfo,
    ToolSetInfo,
)

__all__ = ["ModesInfoMapper", "ModeInfoMapper"]


class ModesInfoMapper:
    @staticmethod
    def from_mappings(modes: list[Mapping[str, Any]]) -> ModesInfo:
        return ModesInfo(modes=[ModeInfoMapper.from_mapping(m) for m in modes])


class ModeInfoMapper:
    @staticmethod
    def from_mapping(mode: Mapping[str, Any]) -> ModeInfo:
        return ModeInfo(
            id=mode["mode_id"],
            code=mode["code"],
            tool_sets=[ToolSetInfoMapper.from_mapping(ts) for ts in mode["tool_sets"]],
        )


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
