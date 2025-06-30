from typing import Protocol

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


engine = create_async_engine("postgresql+asyncpg://report_admin:root@report_db:5433/application_database")
DEFAULT_SESSION_FACTORY = async_sessionmaker(engine)


class IUnitOfWork(Protocol):
    async def __aexit__(self, *args):
        await self.rollback()

    async def commit(self):
        ...

    async def rollback(self):
        ...


class SQLAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        return self.session

    async def __aexit__(self, *args):
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
