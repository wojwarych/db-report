import falcon
import falcon.asgi

from db_report.storage.db import DbConnection
from db_report.storage.engine import engine


class DbReportResource:
    def __init__(self, storage: DbConnection) -> None:
        self._storage = storage

    async def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_TEXT
        try:
            foo = await self._storage.get_ping()
        except Exception as e:
            print(e)
        print(foo)
        resp.text = "Hello!"


app = falcon.asgi.App()
storage = DbConnection(engine)
db_rep_res = DbReportResource(storage)

app.add_route("/hello", db_rep_res)
