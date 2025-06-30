from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .engine import engine, IUnitOfWork
from db_report.core.mappers import TablePagesStats, TopQueries, QueryData

class DbConnection:
    def __init__(self, session):
        self.session = session

    async def get_table_pages(self, table_name: str) -> int:
        page_size = await self.session.execute(
            text(
                "SELECT * FROM pgstattuple(:table_name);"
            ).bindparams(table_name=table_name)
        )
        ret1 = page_size.fetchone()

        return TablePagesStats(
                ret1.table_len,
                ret1.tuple_count,
                ret1.tuple_len,
                ret1.tuple_percent,
                ret1.dead_tuple_count,
                ret1.dead_tuple_len,
                ret1.dead_tuple_percent,
                ret1.free_space,
                ret1.free_percent,
            )

    async def get_top_queries(self):
        page_size = await self.session.execute(
            text(
                """SELECT query, calls, total_exec_time, rows, 100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;"""
            )
        )
        ret1 = page_size.fetchall()

        return TopQueries(queries=[
            QueryData(q.query, q.calls, q.total_exec_time, q.rows, q.hit_percent)
            for q in ret1
        ])
