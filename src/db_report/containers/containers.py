from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker

from db_report.storage.engine import SQLAlchemyUnitOfWork, yield_engine
from db_report.storage.db import DbConnection


class Container(containers.DeclarativeContainer):
    config = providers.Configuration(ini_files=["../config.ini"])

    engine = providers.Callable(
        yield_engine,
        user=config.db.user,
        password=config.db.password,
        host=config.db.host,
        port=config.db.port,
        db_name=config.db.name,
    )

    session_factory = providers.Callable(async_sessionmaker, engine)

    unit_of_work = providers.Factory(
        SQLAlchemyUnitOfWork, session_factory=session_factory
    )

    db_connection = providers.Factory(DbConnection, uow=unit_of_work)
