import typing as t

from src.db_report.core.mappers import (
    DeadTuplesTables,
    TablePagesStats,
    TopQueries,
    TopTables,
)


class IConnection(t.Protocol):
    async def get_table_pages(self, table_name: str) -> TablePagesStats: ...
    async def get_top_queries(self) -> TopQueries: ...
    async def get_top_table_sizes(self) -> TopTables: ...
    async def get_dead_tuples(self) -> DeadTuplesTables: ...
