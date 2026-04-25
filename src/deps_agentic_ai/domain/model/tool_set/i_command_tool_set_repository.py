from typing import Protocol

from .tool_set import ToolSet
from .tool_set_data import ToolSetData

__all__ = ["ICommandToolSetRepository"]


class ICommandToolSetRepository(Protocol):
    async def save(self, tool_set: ToolSet) -> None:
        pass

    async def tool_set_with_code(self, code: str) -> ToolSet | None:
        pass

    async def tool_sets_of_ids_data(self, ids: list[str]) -> list[ToolSetData]:
        pass

    async def tool_sets_of_ids(self, ids: list[str]) -> list[ToolSet]:
        pass

    async def delete_all(self, tool_sets: list[ToolSet]) -> None:
        pass

    async def erase_all(self) -> None:
        pass
