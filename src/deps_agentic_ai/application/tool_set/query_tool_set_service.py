import logging

from deps_agentic_ai.domain.model.tool_set import IQueryToolSetRepository, ToolSetsInfo

__all__ = ["QueryToolSetService"]


class QueryToolSetService:
    def __init__(
        self,
        query_tool_set_repository: IQueryToolSetRepository,
    ) -> None:
        self._query_tool_set_repository = query_tool_set_repository

        self._logger = logging.getLogger(self.__class__.__name__)

    async def find_all(self) -> ToolSetsInfo:
        tool_sets = await self._query_tool_set_repository.find_all()

        self._logger.info("Tool sets found.")

        return tool_sets
