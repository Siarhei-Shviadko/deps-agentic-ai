from typing import TypedDict

from .tool_set import ToolSetInfo

__all__ = ["ModeInfo"]


class ModeInfo(TypedDict):
    id: str
    code: str
    tool_sets: list[ToolSetInfo]
