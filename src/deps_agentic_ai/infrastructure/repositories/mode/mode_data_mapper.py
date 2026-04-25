from typing import Any, Mapping

from deps_agentic_ai.domain.model.mode import ModeData

from ..tool_set import ToolSetDataMapper

__all__ = ["ModeDataMapper"]


class ModeDataMapper:
    @staticmethod
    def from_mapping(mode: Mapping[str, Any]) -> ModeData:
        return ModeData(
            id=mode["mode_id"],
            code=mode["code"],
            tool_sets=[ToolSetDataMapper.from_mapping(ts) for ts in mode["tool_sets"]],
        )
