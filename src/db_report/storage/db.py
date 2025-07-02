import functools
import logging

from sqlalchemy import exc
from sqlalchemy import text

from .engine import IUnitOfWork
from db_report.core.mappers import TablePagesStats, TopQueries, QueryData


class NotFoundError(Exception): ...


def handle_db_exceptions(f):
    @functools.wraps(f)
    async def wrapped(*args, **kwargs):
        try:
            logger = logging.getLogger(f"{__name__}")
            return await f(*args, **kwargs)
        except exc.ProgrammingError as e:
            logger.info("%s", e.orig)
            raise NotFoundError("Resource not found!")

    return wrapped


class DbConnection:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    @handle_db_exceptions
    async def get_table_pages(self, table_name: str) -> int:
        async with self.uow:
            page_size = await self.uow.session.execute(
                text("SELECT * FROM pgstattuple(:table_name);").bindparams(
                    table_name=table_name
                )
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

    @handle_db_exceptions
    async def get_top_queries(self):
        async with self.uow:
            page_size = await self.uow.session.execute(
                text(
                    """SELECT query, calls, total_exec_time, rows, 100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;"""
                )
            )
            ret1 = page_size.fetchall()

            return TopQueries(
                queries=[
                    QueryData(
                        q.query, q.calls, q.total_exec_time, q.rows, q.hit_percent
                    )
                    for q in ret1
                ]
            )
