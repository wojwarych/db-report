from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine


def yield_engine(
    user: str, password: str, host: str, port: int, db_name: str
) -> AsyncEngine:
    return create_async_engine(
        f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}",
    )


class IUnitOfWork(Protocol):
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.rollback()

    async def commit(self): ...

    async def rollback(self): ...


class SQLAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session_factory: AsyncSession):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
