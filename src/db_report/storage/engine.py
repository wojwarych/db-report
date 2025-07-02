"""Module for providing connection with Storage engine and transactional Session"""

from types import TracebackType
from typing import Protocol, Self

from dependency_injector import providers
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine


def yield_engine(
    user: str, password: str, host: str, port: int, db_name: str
) -> AsyncEngine:
    """
    Function for containers.Container to make callable configuration of Singleton engine
    """
    return create_async_engine(
        f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}",
    )


class IUnitOfWork(Protocol):
    """Interface definition for creating Unit of Work pattern.
    Used for communication with DBs for repository (i.e. storage) instances
    """

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException | None,
        traceback: TracebackType,
    ) -> None:
        await self.rollback()

    async def commit(self) -> None: ...  # pylint: disable=missing-function-docstring

    async def rollback(self) -> None: ...  # pylint: disable=missing-function-docstring


class SQLAlchemyUnitOfWork(IUnitOfWork):
    """SQLAlchemy implementation of IUnitoOfWork interface for communicating with DB"""

    def __init__(self, session_factory: providers.Callable[AsyncSession]):
        self.session_factory = session_factory

    async def __aenter__(self) -> Self:
        """Implements context manager that creates AsyncSession for given context"""
        self.session = self.session_factory()  # pylint: disable=attribute-defined-outside-init
        return await super().__aenter__()

    async def __aexit__(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException | None,
        traceback: TracebackType,
    ) -> None:
        """Implements exiting context manager for IUnitOfWork interface"""
        await super().__aexit__(exc_type, exc_value, traceback)
        await self.session.close()

    async def commit(self) -> None:
        """Runs commit method on the session object. Should be used inside ctx manager"""
        await self.session.commit()

    async def rollback(self) -> None:
        """Rollbacks all the changes made inside the session"""
        await self.session.rollback()
