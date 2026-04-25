from typing import TypedDict

from .tool_info import ToolInfo

__all__ = ["ToolSetInfo"]


class ToolSetInfo(TypedDict):
    id: str
    code: str
    name: str
    tools: list[ToolInfo]
