from typing import TypedDict

from .tool_data import ToolData

__all__ = ["ToolSetData"]


class ToolSetData(TypedDict):
    id: str
    code: str
    name: str
    tools: list[ToolData]
