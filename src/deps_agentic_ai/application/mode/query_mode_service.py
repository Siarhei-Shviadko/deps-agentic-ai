import logging

from deps_agentic_ai.domain.model.mode import (
    IQueryModeRepository,
    ModeFiltering,
    ModesInfo,
)

__all__ = ["QueryModeService"]


class QueryModeService:
    def __init__(
        self,
        query_mode_repository: IQueryModeRepository,
    ) -> None:
        self._query_mode_repository = query_mode_repository

        self._logger = logging.getLogger(self.__class__.__name__)

    async def find_all(self, code: str | None = None) -> ModesInfo:
        modes = await self._query_mode_repository.find_all(filtering=ModeFiltering(code=code))

        self._logger.info("Modes found.")

        return modes
