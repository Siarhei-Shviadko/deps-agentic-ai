from typing import Any, Mapping

from deps_agentic_ai.domain.model.conversation import ToolSet

from .tool_mapper import ToolMapper

__all__ = ["ToolSetMapper"]


class ToolSetMapper:
    @staticmethod
    def from_mapping(tool_set: Mapping[str, Any]) -> ToolSet:
        tools = [ToolMapper.from_mapping(tool_data) for tool_data in tool_set.get("tools") or []]

        return ToolSet(id_=tool_set["tool_set_id"], code=tool_set["code"], name=tool_set["name"], tools=tools)
