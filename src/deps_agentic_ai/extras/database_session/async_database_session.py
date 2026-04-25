import logging
from asyncio import current_task
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import MetaData, text
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from .settings import DatabaseSettings

__all__ = ["AsyncDatabaseSession", "metadata"]


metadata = MetaData()


class AsyncDatabaseSession:  # noqa: WPS230
    def __init__(self) -> None:
        settings = DatabaseSettings()

        engine_url = URL(
            drivername=f"{settings.dialect.value}+{settings.driver.value}",
            username=settings.user,
            password=settings.password,
            host=settings.host,
            port=settings.port,
            database=settings.db,
            query={},
        )

        self.engine = create_async_engine(
            engine_url,
            pool_size=settings.pool_size,
            connect_args={
                "sslcert": settings.ssl.sslcert,
                "sslkey": settings.ssl.sslkey,
                "sslmode": settings.ssl.sslmode,
                "sslrootcert": settings.ssl.sslrootcert,
            }
            if settings.require_secure_transport
            else {},
            execution_options={"isolation_level": "REPEATABLE READ"},
        )

        self.session_factory = async_scoped_session(
            session_factory=async_sessionmaker(self.engine, class_=AsyncSession),
            scopefunc=current_task,
        )

        self._logger = logging.getLogger(self.__class__.__name__)

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[AsyncSession, None]:
        self.session_factory()

        try:
            yield self.session_factory
            await self.session_factory.commit()

        except Exception as e:
            await self.session_factory.rollback()
            raise e

        finally:
            await self.session_factory.remove()

    async def healthcheck(self):
        async with self.connection() as conn:
            await conn.execute(text("select 1;"))
