"""
Module that implements repository functionalities to fetch stats about DB performance
"""

import functools
import logging
import typing as t

from sqlalchemy import exc, text

from db_report.core.mappers import (
    DeadTuples,
    DeadTuplesTables,
    QueryData,
    Table,
    TablePagesStats,
    TopQueries,
    TopTables,
)

from .engine import IUnitOfWork

Param = t.ParamSpec("Param")
RetType = t.TypeVar("RetType")


class NotFoundError(Exception): ...  # pylint: disable=missing-class-docstring


def handle_db_exceptions(
    f: t.Callable[Param, t.Awaitable[RetType]],
) -> t.Callable[Param, t.Awaitable[RetType]]:
    """Decorator that wraps DB exceptions and propagates them in more suitable manner"""

    @functools.wraps(f)
    async def wrapped(*args: Param.args, **kwargs: Param.kwargs) -> RetType:
        logger = logging.getLogger(f"{__name__}")
        try:
            return await f(*args, **kwargs)
        except exc.ProgrammingError as e:
            logger.info("%s", e.orig)
            raise NotFoundError("Resource not found!") from e

    return wrapped


class DbConnection:
    """
    Repository-like class that provides communication to
    statistic resources for Postgres DB
    """

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    @handle_db_exceptions
    async def get_table_pages(self, table_name: str) -> TablePagesStats:
        """Get statistics about page density for given table"""
        async with self.uow:
            page_size = await self.uow.session.execute(  # type: ignore[attr-defined]
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
    async def get_top_queries(self) -> TopQueries:
        """Returns statistics about most often called queries"""
        async with self.uow:
            page_size = await self.uow.session.execute(  # type: ignore[attr-defined]
                text(
                    """SELECT query, calls, total_exec_time, rows,
100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0)
AS hit_percent FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;"""
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

    @handle_db_exceptions
    async def get_top_table_sizes(self) -> TopTables:
        """Returns statistics about biggest tables in size"""
        async with self.uow:
            table_sizes = await self.uow.session.execute(  # type: ignore[attr-defined]
                text(
                    """SELECT
relname AS relation, pg_size_pretty(pg_total_relation_size(C.oid))
AS total_size, pg_size_pretty(pg_relation_size(C.oid)) AS table_size
FROM pg_class C LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
WHERE nspname NOT IN ('pg_catalog', 'information_schema')
AND C.relkind <> 'i' AND nspname !~ '^pg_toast'
ORDER BY pg_total_relation_size (C.oid) DESC LIMIT 10;"""
                )
            )
            ret1 = table_sizes.fetchall()

            return TopTables(
                tables=[Table(q.relation, q.total_size, q.table_size) for q in ret1]
            )

    @handle_db_exceptions
    async def get_dead_tuples(self) -> DeadTuplesTables:
        """Returns statistics about biggest tables in size"""
        async with self.uow:
            dead_tuples = await self.uow.session.execute(  # type: ignore[attr-defined]
                text(
                    """SELECT
relname AS tablename, n_dead_tup AS dead_tuples, n_live_tup AS alive_tuples
FROM pg_stat_all_tables WHERE schemaname = 'public'
ORDER BY dead_tuples DESC LIMIT 10;"""
                )
            )
            ret1 = dead_tuples.fetchall()

            return DeadTuplesTables(
                tables=[
                    DeadTuples(q.tablename, q.dead_tuples, q.alive_tuples) for q in ret1
                ]
            )
