from typing import TypedDict

from .parameter_data import ParameterData

__all__ = ["ToolData"]


class ToolData(TypedDict):
    code: str
    name: str
    parameters: list[ParameterData]
