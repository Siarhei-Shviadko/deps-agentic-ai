from typing import Any, Mapping

from deps_agentic_ai.domain.model.conversation import Mode

from .tool_set_mapper import ToolSetMapper

__all__ = ["ModeMapper"]


class ModeMapper:
    @staticmethod
    def from_mapping(mode: Mapping[str, Any]) -> Mode:
        tool_sets = [ToolSetMapper.from_mapping(tool_set_data) for tool_set_data in mode.get("tool_sets") or []]

        return Mode(id_=mode["id"], code=mode["code"], tool_sets=tool_sets)
