from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .engine import engine

class DbConnection:
    def __init__(self, engine):
        self._engine = engine

    async def get_ping(self) -> int:
        async with AsyncSession(self._engine) as sess:
            async with sess.begin():
                stats = await sess.execute(
                    text("SELECT * FROM pg_stat_statements;")
                )
                ret1 = ret.fetchone()

        return ret1

    async def get_table_pages(self, table_name: str) -> int:
        async with AsyncSession(self._engine) as sess:
            async with sess.begin():
                page_size = await sess.execute(
                    text(
                        "SELECT relpages FROM pg_class WHERE relname = :table_name;"
                    ).bindparams(table_name=table_name)
                )
                ret1 = page_size.fetchone()

        return ret1
