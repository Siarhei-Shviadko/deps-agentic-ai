from typing import TypedDict

from ...shared import ToolSetCode
from .active_tool_data import ActiveToolData

__all__ = ["ContextData"]


class ContextData(TypedDict):
    tools: dict[ToolSetCode, list[ActiveToolData]]
