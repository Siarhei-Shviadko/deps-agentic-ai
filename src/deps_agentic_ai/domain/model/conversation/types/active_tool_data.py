from typing import TypedDict

from .argument_data import ArgumentData

__all__ = ["ActiveToolData"]


class ActiveToolData(TypedDict):
    code: str
    arguments: list[ArgumentData]
