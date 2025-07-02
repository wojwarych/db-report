"""Module holding mappers for DB to application objects"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TablePagesStats:  # pylint: disable=too-many-instance-attributes
    """Class returning stats for table pages"""

    table_len: int
    tuple_count: int
    tuple_len: int
    tuple_percent: int
    dead_tuple_count: int
    dead_tuple_len: int
    dead_tuple_percent: int
    free_space: int
    free_percent: int


@dataclass(frozen=True)
class QueryData:
    """Class returning stats for particular query"""

    query: str
    calls: int
    total_exec_time: int
    rows: int
    hit_percent: float


@dataclass(frozen=True)
class TopQueries:
    """Class returning list of query stats"""

    queries: list[QueryData]
