from typing import TypedDict

from .tool_set_info import ToolSetInfo

__all__ = ["ToolSetsInfo"]


class ToolSetsInfo(TypedDict):
    tool_sets: list[ToolSetInfo]
