from typing import Protocol

from .mode_filtering import ModeFiltering
from .modes_info import ModesInfo

__all__ = ["IQueryModeRepository"]


class IQueryModeRepository(Protocol):
    async def find_all(self, filtering: ModeFiltering | None = None) -> ModesInfo:
        pass
