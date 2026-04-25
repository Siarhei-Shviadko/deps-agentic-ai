from typing import TypedDict

from ..tool_set import ToolSetData

__all__ = ["ModeData"]


class ModeData(TypedDict):
    id: str
    code: str
    tool_sets: list[ToolSetData]
