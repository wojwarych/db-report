from sqlalchemy import text

from .engine import engine

class DbConnection:
    def __init__(self, engine):
        self._engine = engine

    async def get_ping(self) -> int:
        async with self._engine.connect() as conn:
            ret = await conn.execute(text("SELECT * FROM pg_stat_statements;"))
            ret1 = ret.fetchone()

        return ret1


