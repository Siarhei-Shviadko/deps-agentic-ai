from typing import Any, Mapping

from deps_agentic_ai.domain.model.conversation import ActiveTool

from .argument_mapper import ArgumentMapper

__all__ = ["ActiveToolMapper"]


class ActiveToolMapper:
    @staticmethod
    def from_mapping(tool: Mapping[str, Any]) -> ActiveTool:
        return ActiveTool(
            code=tool["code"],
            arguments=[ArgumentMapper.from_mapping(arg) for arg in tool["arguments"]],
        )

    @staticmethod
    def to_dict(tool: ActiveTool) -> dict[str, Any]:
        return {
            "code": tool.code,
            "arguments": [ArgumentMapper.to_dict(arg) for arg in tool.arguments],
        }
