import logging

from deps_agentic_ai.domain.model.agent_vendor import (
    AgentVendorsInfo,
    IQueryAgentVendorRepository,
)

__all__ = ["QueryAgentVendorService"]


class QueryAgentVendorService:
    def __init__(
        self,
        query_agent_vendor_repository: IQueryAgentVendorRepository,
    ) -> None:
        self._query_agent_vendor_repository = query_agent_vendor_repository

        self._logger = logging.getLogger(self.__class__.__name__)

    async def find_all(self) -> AgentVendorsInfo:
        return await self._query_agent_vendor_repository.find_all()
