from dependency_injector import containers, providers
from db_report.storage.engine import SQLAlchemyUnitOfWork
from db_report.storage.db import DbConnection


class Container(containers.DeclarativeContainer):
    unit_of_work = providers.Singleton(SQLAlchemyUnitOfWork)

    db_connection = providers.Factory(DbConnection, session=unit_of_work)
