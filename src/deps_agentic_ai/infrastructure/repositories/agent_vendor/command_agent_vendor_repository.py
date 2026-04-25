from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from deps_agentic_ai.domain.model.agent_vendor import (
    AgentVendor,
    ICommandAgentVendorRepository,
)

from ..tables import agent_vendor_table
from .mappers import AgentVendorMapper

__all__ = ["UoWCommandAgentVendorRepository"]


class UoWCommandAgentVendorRepository(ICommandAgentVendorRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, agent_vendor: AgentVendor) -> None:
        insert_query = insert(agent_vendor_table)
        save_query = insert_query.on_conflict_do_update(
            constraint=agent_vendor_table.primary_key,
            set_=dict(insert_query.excluded),
        ).values(**AgentVendorMapper.to_dict(agent_vendor))

        await self._session.execute(save_query)

    async def save_all(self, agent_vendors: list[AgentVendor]) -> None:
        insert_query = insert(agent_vendor_table)
        save_query = insert_query.on_conflict_do_update(
            constraint=agent_vendor_table.primary_key, set_=dict(active=insert_query.excluded["active"])
        )
        raw_data = [AgentVendorMapper.to_dict(agent_vendor) for agent_vendor in agent_vendors]

        await self._session.execute(save_query, raw_data)

    async def agent_vendor_of_id(self, id_: str) -> AgentVendor | None:
        query = select(agent_vendor_table).where(agent_vendor_table.c.id == id_)
        result = await self._session.execute(query)

        return AgentVendorMapper.from_mapping(result.mappings().first()) if self._has_rows(result) else None

    async def active_agent_vendor(self) -> AgentVendor | None:
        query = select(agent_vendor_table).where(agent_vendor_table.c.active)
        result = await self._session.execute(query)

        return AgentVendorMapper.from_mapping(result.mappings().first()) if self._has_rows(result) else None

    async def has_agent_vendor_with_name(self, name: str) -> bool:
        query = select(agent_vendor_table.c.id).where(agent_vendor_table.c.name == name)
        result = await self._session.execute(query)

        return self._has_rows(result)

    async def delete(self, agent_vendor: AgentVendor) -> None:
        query = delete(agent_vendor_table).where(agent_vendor_table.c.id == agent_vendor.id())
        await self._session.execute(query)

    async def _erase_all(self) -> None:
        query = delete(agent_vendor_table)

        await self._session.execute(query)

    @staticmethod
    def _has_rows(result: CursorResult) -> bool:
        return result.rowcount > 0
