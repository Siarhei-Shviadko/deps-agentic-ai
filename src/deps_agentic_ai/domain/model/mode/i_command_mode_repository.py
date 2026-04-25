from typing import Protocol

from .mode import Mode
from .mode_data import ModeData

__all__ = ["ICommandModeRepository"]


class ICommandModeRepository(Protocol):
    async def has_mode_with_code(self, code: str) -> bool:
        pass

    async def save(self, mode: Mode) -> None:
        pass

    async def mode_of_id_data(self, id_: str) -> ModeData | None:
        pass

    async def modes_of_ids(self, ids: list[str]) -> list[Mode]:
        pass

    async def mode_of_id(self, id_: str) -> Mode | None:
        pass

    async def delete_all(self, modes: list[Mode]) -> None:
        pass

    async def erase_all(self) -> None:
        pass
