from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine("postgresql+asyncpg://report_admin:root@report_db:5433/application_database")
