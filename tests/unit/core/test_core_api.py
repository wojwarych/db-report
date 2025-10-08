# pylint: disable=missing-module-docstring, missing-function-docstring
import random

import pytest
from faker import Faker
from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import exc

from src.db_report.core.core_api import DBStats
from src.db_report.core.mappers import (
    DeadTuples,
    DeadTuplesTables,
    QueryData,
    Table,
    TablePagesStats,
    TopQueries,
    TopTables,
)
from src.db_report.storage.db import NotFoundError, handle_db_exceptions
from src.db_report.storage.storage_base import IConnection

fake = Faker()


class FakeConnection(IConnection):
    """Fake connection class that implements interface for DB connection"""

    def __init__(
        self, with_err: bool = False, exc_type: Exception | None = None
    ) -> None:
        self.with_err = with_err
        self.exc_type = exc_type

    @handle_db_exceptions
    async def get_table_pages(self, table_name: str) -> TablePagesStats:
        if self.with_err and self.exc_type is not None:
            raise self.exc_type
        return TablePagesStats(
            table_len=fake.pyint(),
            tuple_count=fake.pyint(),
            tuple_len=fake.pyint(),
            tuple_percent=fake.pyint(),
            dead_tuple_count=fake.pyint(),
            dead_tuple_len=fake.pyint(),
            dead_tuple_percent=fake.pyint(),
            free_space=fake.pyint(),
            free_percent=fake.pyint(),
        )

    async def get_top_queries(self) -> TopQueries:
        return TopQueries(
            [
                QueryData(
                    query=fake.pystr(),
                    calls=fake.pyint(),
                    total_exec_time=fake.pyint(),
                    rows=fake.pyint(),
                    hit_percent=fake.pyfloat(),
                )
                for i in range(random.randrange(10))
            ]
        )

    async def get_top_table_sizes(self) -> TopTables:
        return TopTables(
            [
                Table(
                    relation=fake.pystr(),
                    total_size=fake.pystr(),
                    table_size=fake.pystr(),
                )
                for i in range(random.randrange(10))
            ]
        )

    async def get_dead_tuples(self) -> DeadTuplesTables:
        return DeadTuplesTables(
            [
                DeadTuples(
                    tablename=fake.pystr(),
                    dead_tuples=fake.pyint(),
                    alive_tuples=fake.pyint(),
                )
                for i in range(random.randrange(10))
            ]
        )


@given(st.text())
async def test_get_table_pages_returns_data(text: str) -> None:
    db_stats = DBStats(connection=FakeConnection())

    ret = await db_stats.get_table_pages(text)

    assert ret is not None
    assert isinstance(ret, TablePagesStats)


@given(st.text())
async def test_get_table_pages_returns_none_on_programming_error(text: str) -> None:
    fc = FakeConnection(
        with_err=True,
        exc_type=exc.ProgrammingError(
            "Could not find table!", params=None, orig=Exception()
        ),
    )
    db_stats = DBStats(connection=fc)

    with pytest.raises(NotFoundError):
        await db_stats.get_table_pages(text)


async def test_get_dead_tuples() -> None:
    db_stats = DBStats(connection=FakeConnection())

    ret = await db_stats.get_dead_tuples()

    assert ret is not None
    assert ret.tables != []
    assert isinstance(ret, DeadTuplesTables)


async def test_get_top_queries() -> None:
    db_stats = DBStats(connection=FakeConnection())

    ret = await db_stats.get_top_queries()

    assert ret is not None
    assert ret.queries != []
    assert isinstance(ret, TopQueries)


async def test_get_top_table_sizes() -> None:
    db_stats = DBStats(connection=FakeConnection())

    ret = await db_stats.get_top_table_sizes()

    assert ret is not None
    assert ret.tables != []
    assert isinstance(ret, TopTables)
