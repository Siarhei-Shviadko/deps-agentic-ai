from typing import TypedDict

from .mode_info import ModeInfo

__all__ = ["ModesInfo"]


class ModesInfo(TypedDict):
    modes: list[ModeInfo]
