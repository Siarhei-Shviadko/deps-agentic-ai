from typing import Protocol

from .tool_sets_info import ToolSetsInfo

__all__ = ["IQueryToolSetRepository"]


class IQueryToolSetRepository(Protocol):
    async def find_all(self) -> ToolSetsInfo:
        pass
