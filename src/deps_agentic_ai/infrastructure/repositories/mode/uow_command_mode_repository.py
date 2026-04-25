from sqlalchemy import (
    Column,
    asc,
    cast,
    delete,
    desc,
    func,
    literal,
    literal_column,
    select,
)
from sqlalchemy.dialects.postgresql import JSONB, aggregate_order_by, insert
from sqlalchemy.ext.asyncio import AsyncSession

from deps_agentic_ai.domain.model.mode import ICommandModeRepository, Mode, ModeData

from ..tables import mode_table, tool_set_table
from .mode_data_mapper import ModeDataMapper
from .mode_mapper import ModeMapper, ModesMapper

__all__ = ["UoWCommandModeRepository"]


class UoWCommandModeRepository(ICommandModeRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @property
    def mode_columns(self) -> list[Column]:
        return [
            mode_table.c.mode_id,
            mode_table.c.code,
            mode_table.c.created_at,
            func.coalesce(
                cast(
                    func.json_agg(
                        aggregate_order_by(
                            func.json_build_object(
                                "tool_set_id",
                                tool_set_table.c.tool_set_id,
                                "code",
                                tool_set_table.c.code,
                                "name",
                                tool_set_table.c.name,
                                "tools",
                                tool_set_table.c.tools,
                            ),
                            asc(tool_set_table.c.created_at),
                        ),
                    ).filter(tool_set_table.c.tool_set_id.isnot(None)),
                    JSONB,
                ),
                literal("[]").cast(JSONB),
            ).label("tool_sets"),
        ]

    @property
    def joined_mode_tables(self) -> list[Column]:
        tool_set_ids_table = (
            func.jsonb_array_elements_text(mode_table.c.tool_set_ids).table_valued("value").alias("tool_set_ids_table")
        )

        return mode_table.outerjoin(
            tool_set_ids_table,
            literal_column("true"),
        ).outerjoin(tool_set_table, tool_set_ids_table.c.value == tool_set_table.c.tool_set_id)

    async def has_mode_with_code(self, code: str) -> bool:
        query = select(mode_table.c.mode_id).where(mode_table.c.code == code)
        rows = await self._session.execute(query)

        return rows.rowcount >= 1

    async def save(self, mode: Mode) -> None:
        insert_query = insert(mode_table)
        save_query = insert_query.on_conflict_do_update(
            constraint=mode_table.primary_key,
            set_=dict(insert_query.excluded),
        ).values(**ModeMapper.to_dict(mode))

        await self._session.execute(save_query)

    async def mode_of_id_data(self, id_: str) -> ModeData | None:
        query = (
            select(*self.mode_columns)
            .where(mode_table.c.mode_id == id_)
            .select_from(self.joined_mode_tables)
            .group_by(mode_table.c.mode_id, mode_table.c.code, mode_table.c.created_at)
            .distinct()
        )
        rows = await self._session.execute(query)

        if rows.rowcount < 1:
            return None

        return ModeDataMapper.from_mapping(rows.mappings().first())

    async def modes_of_ids(self, ids: list[str]) -> list[Mode]:
        query = (
            select(*self.mode_columns)
            .select_from(self.joined_mode_tables)
            .where(mode_table.c.mode_id.in_(ids))
            .order_by(desc(mode_table.c.created_at))
            .group_by(mode_table.c.mode_id, mode_table.c.code, mode_table.c.created_at)
            .distinct()
        )

        rows = await self._session.execute(query)

        return ModesMapper.from_mappings(rows.mappings().fetchall())

    async def mode_of_id(self, id_: str) -> Mode | None:
        query = (
            select(*self.mode_columns)
            .where(mode_table.c.mode_id == id_)
            .select_from(self.joined_mode_tables)
            .group_by(mode_table.c.mode_id, mode_table.c.code, mode_table.c.created_at)
            .distinct()
        )
        rows = await self._session.execute(query)

        if rows.rowcount < 1:
            return None

        return ModeMapper.from_mapping(rows.mappings().first())

    async def delete_all(self, modes: list[Mode]) -> None:
        query = delete(mode_table).where(
            mode_table.c.mode_id.in_({m.id() for m in modes}),
        )

        await self._session.execute(query)

    async def erase_all(self) -> None:
        query = delete(mode_table)

        await self._session.execute(query)
