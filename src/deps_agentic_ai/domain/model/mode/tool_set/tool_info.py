from typing import TypedDict

from .parameter_info import ParameterInfo

__all__ = ["ToolInfo"]


class ToolInfo(TypedDict):
    code: str
    name: str
    parameters: list[ParameterInfo]
