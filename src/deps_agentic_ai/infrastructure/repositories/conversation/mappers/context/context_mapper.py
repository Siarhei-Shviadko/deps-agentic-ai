from typing import Any, Mapping

from deps_agentic_ai.domain.model.conversation import Context

from .active_tool_mapper import ActiveToolMapper

__all__ = ["ContextMapper"]


class ContextMapper:
    @staticmethod
    def from_mapping(context: Mapping[str, Any]) -> Context:
        return Context(
            tools={
                tool_set_code: [ActiveToolMapper.from_mapping(tool) for tool in tools]
                for tool_set_code, tools in context.items()
            }
        )

    @staticmethod
    def to_dict(context: Context) -> dict[str, Any]:
        return {
            tool_set_code: [ActiveToolMapper.to_dict(tool) for tool in tools]
            for tool_set_code, tools in context.tools.items()
        }
