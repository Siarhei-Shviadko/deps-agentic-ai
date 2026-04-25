from sqlalchemy.ext.asyncio import AsyncSession

from deps_agentic_ai.extras import AsyncDatabaseSession

from ..repositories import (
    UoWCommandAgentVendorRepository,
    UoWCommandConversationRepository,
    UoWCommandModeRepository,
    UoWCommandToolSetRepository,
)
from .abstract_unit_of_work import AbstractUnitOfWork

__all__ = ["SqlAlchemyUnitOfWork"]


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    _session: AsyncSession

    def __init__(self, database_session: AsyncDatabaseSession) -> None:
        self._database_session = database_session

    async def __aenter__(self) -> None:
        self._session = self._database_session.session_factory()
        self.tool_sets = UoWCommandToolSetRepository(self._session)
        self.modes = UoWCommandModeRepository(self._session)
        self.agent_vendors = UoWCommandAgentVendorRepository(self._session)
        self.conversations = UoWCommandConversationRepository(self._session)

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type is not None:
            await self.rollback()

        await self._session.close()
        await self._database_session.session_factory.remove()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
