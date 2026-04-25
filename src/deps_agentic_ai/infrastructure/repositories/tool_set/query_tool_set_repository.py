from sqlalchemy import Column, desc, select

from deps_agentic_ai.domain.model.tool_set import IQueryToolSetRepository, ToolSetsInfo
from deps_agentic_ai.extras import AsyncDatabaseSession

from ..tables import tool_set_table
from .tool_set_info_mapper import ToolSetsInfoMapper

__all__ = ["QueryToolSetRepository"]


class QueryToolSetRepository(IQueryToolSetRepository):
    def __init__(self, database: AsyncDatabaseSession) -> None:
        self._db = database

    @property
    def tool_set_columns(self) -> list[Column]:
        return [
            tool_set_table.c.tool_set_id,
            tool_set_table.c.code,
            tool_set_table.c.name,
            tool_set_table.c.tools,
            tool_set_table.c.created_at,
        ]

    async def find_all(self) -> ToolSetsInfo:
        query = select(*self.tool_set_columns).order_by(desc(tool_set_table.c.created_at))

        async with self._db.connection() as conn:
            rows = await conn.execute(query)

        return ToolSetsInfoMapper.from_mappings(rows.mappings())
