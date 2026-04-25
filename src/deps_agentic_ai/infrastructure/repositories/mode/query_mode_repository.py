from sqlalchemy import Column, asc, cast, desc, func, literal, literal_column, select
from sqlalchemy.dialects.postgresql import JSONB, aggregate_order_by
from sqlalchemy.orm import Query

from deps_agentic_ai.domain.model.mode import (
    IQueryModeRepository,
    ModeFiltering,
    ModesInfo,
)
from deps_agentic_ai.extras import AsyncDatabaseSession

from ..tables import mode_table, tool_set_table
from .mode_info_mapper import ModesInfoMapper

__all__ = ["QueryModeRepository"]


class QueryModeRepository(IQueryModeRepository):
    def __init__(self, database: AsyncDatabaseSession) -> None:
        self._db = database

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

    async def find_all(self, filtering: ModeFiltering | None = None) -> ModesInfo:
        query = (
            select(*self.mode_columns)
            .select_from(self.joined_mode_tables)
            .order_by(desc(mode_table.c.created_at))
            .group_by(mode_table.c.mode_id, mode_table.c.code, mode_table.c.created_at)
            .distinct()
        )

        if filtering:
            query = self._apply_filtering(query, filtering)

        async with self._db.connection() as conn:
            rows = await conn.execute(query)

        return ModesInfoMapper.from_mappings(rows.mappings())

    def _apply_filtering(self, query: Query, filtering: ModeFiltering) -> Query:
        if filtering.code is not None:
            query = query.where(mode_table.c.code == filtering.code)

        return query
