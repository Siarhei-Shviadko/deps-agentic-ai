from sqlalchemy import Column, delete, desc, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from deps_agentic_ai.domain.model.tool_set import (
    ICommandToolSetRepository,
    ToolSet,
    ToolSetData,
)

from ..tables import tool_set_table
from .tool_set_data_mapper import ToolSetsDataMapper
from .tool_set_mapper import ToolSetMapper, ToolSetsMapper

__all__ = ["UoWCommandToolSetRepository"]


class UoWCommandToolSetRepository(ICommandToolSetRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @property
    def tool_set_columns(self) -> list[Column]:
        return [
            tool_set_table.c.tool_set_id,
            tool_set_table.c.code,
            tool_set_table.c.name,
            tool_set_table.c.tools,
            tool_set_table.c.created_at,
        ]

    async def save(self, tool_set: ToolSet) -> None:
        insert_query = insert(tool_set_table)
        save_query = insert_query.on_conflict_do_update(
            constraint=tool_set_table.primary_key,
            set_=dict(insert_query.excluded),
        ).values(**ToolSetMapper.to_dict(tool_set))

        await self._session.execute(save_query)

    async def tool_set_with_code(self, code: str) -> ToolSet | None:
        query = select(*self.tool_set_columns).where(tool_set_table.c.code == code)

        rows = await self._session.execute(query)

        if rows.rowcount < 1:
            return None

        return ToolSetMapper.from_mapping(rows.mappings().first())

    async def tool_sets_of_ids_data(self, ids: list[str]) -> list[ToolSetData]:
        query = select(*self.tool_set_columns).where(tool_set_table.c.tool_set_id.in_(ids))

        rows = await self._session.execute(query)

        return ToolSetsDataMapper.from_mappings(rows.mappings().fetchall())

    async def tool_sets_of_ids(self, ids: list[str]) -> list[ToolSet]:
        query = (
            select(*self.tool_set_columns)
            .where(tool_set_table.c.tool_set_id.in_(ids))
            .order_by(desc(tool_set_table.c.created_at))
        )

        rows = await self._session.execute(query)

        return ToolSetsMapper.from_mappings(rows.mappings().fetchall())

    async def delete_all(self, tool_sets: list[ToolSet]) -> None:
        query = delete(tool_set_table).where(
            tool_set_table.c.tool_set_id.in_({ts.id() for ts in tool_sets}),
        )

        await self._session.execute(query)

    async def erase_all(self) -> None:
        query = delete(tool_set_table)

        await self._session.execute(query)
