from sqlalchemy import select

from deps_agentic_ai.domain.model.agent_vendor import (
    AgentVendorsInfo,
    IQueryAgentVendorRepository,
)
from deps_agentic_ai.extras import AsyncDatabaseSession

from ..tables import agent_vendor_table
from .mappers import AgentVendorsInfoMapper

__all__ = ["QueryAgentVendorRepository"]


class QueryAgentVendorRepository(IQueryAgentVendorRepository):
    def __init__(self, database: AsyncDatabaseSession) -> None:
        self._db = database

    async def find_all(self) -> AgentVendorsInfo:
        query = select(agent_vendor_table)

        async with self._db.connection() as conn:
            rows = await conn.execute(query)

        return AgentVendorsInfoMapper.from_mappings(rows.mappings())
