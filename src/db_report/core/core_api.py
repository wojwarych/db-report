"""Core API for collecting specific statistics of database"""

from db_report.core.mappers import (
    DeadTuplesTables,
    TablePagesStats,
    TopQueries,
    TopTables,
)
from db_report.storage.db import DbConnection


class DBStats:
    def __init__(self, connection: DbConnection) -> None:
        self._connection = connection

    async def get_table_pages(self, table_name: str) -> TablePagesStats:
        return await self._connection.get_table_pages(table_name)

    async def get_top_queries(self) -> TopQueries:
        return await self._connection.get_top_queries()

    async def get_top_table_sizes(self) -> TopTables:
        return await self._connection.get_top_table_sizes()

    async def get_dead_tuples(self) -> DeadTuplesTables:
        return await self._connection.get_dead_tuples()
