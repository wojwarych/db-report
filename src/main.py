import json
import decimal
from dataclasses import asdict, is_dataclass
from functools import partial

import falcon
import falcon.asgi
from falcon import media

from db_report.storage.db import DbConnection
from db_report.storage.engine import engine


class DataClassSerializer(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super().default(o)


dataclasses_json_serializer = media.JSONHandler(
    dumps=partial(json.dumps, cls=DataClassSerializer),
)
extra_handlers = {
    "application/json": dataclasses_json_serializer
}


class DbReportResource:
    def __init__(self, storage: DbConnection) -> None:
        self._storage = storage

    async def on_get_table_pages(self, req, resp, table_name: str):
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_JSON
        try:
            foo = await self._storage.get_table_pages(table_name)
        except Exception as e:
            print(e)
        resp.media = foo

    async def on_get_top_queries(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_JSON
        try:
            foo = await self._storage.get_top_queries()
        except Exception as e:
            print(e)
        resp.media = foo



app = falcon.asgi.App()

app.resp_options.media_handlers.update(extra_handlers)
storage = DbConnection(engine)
db_rep_res = DbReportResource(storage)

app.add_route("/page/{table_name}", db_rep_res, suffix="table_pages")
app.add_route("/queries/top", db_rep_res, suffix="top_queries")
