import json
import decimal
from dataclasses import asdict, is_dataclass
from functools import partial

import falcon
import falcon.asgi
from dependency_injector.wiring import Provide, inject
from falcon import media
import uvicorn

from db_report.storage.db import DbConnection
from db_report.storage.engine import IUnitOfWork, SQLAlchemyUnitOfWork
from db_report.containers.containers import Container


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
extra_handlers = {"application/json": dataclasses_json_serializer}


class DbReportResource:
    @inject
    async def on_get_table_pages(
        self,
        req,
        resp,
        table_name: str,
        db_connection: DbConnection = Provide[Container.db_connection],
    ):
        try:
            data = await db_connection.get_table_pages(table_name)
        except Exception as e:
            resp.status = falcon.HTTP_404
            resp.content_type = falcon.MEDIA_TEXT
            resp.text = f"Could not access table {table_name}!"
        else:
            resp.status = falcon.HTTP_200
            resp.content_type = falcon.MEDIA_JSON
            resp.media = data

    @inject
    async def on_get_top_queries(
        self, req, resp, db_connection: DbConnection = Provide[Container.db_connection]
    ):
        try:
            data = await db_connection.get_top_queries()
        except Exception as e:
            resp.status = falcon.HTTP_404
            resp.content_type = falcon.MEDIA_TEXT
            resp.text = "Could not access data!"
        else:
            resp.status = falcon.HTTP_200
            resp.content_type = falcon.MEDIA_JSON
            resp.media = data


container = Container()
container.wire(modules=[__name__])

app = falcon.asgi.App()
app.resp_options.media_handlers.update(extra_handlers)
db_rep_res = DbReportResource()
app.add_route("/page/{table_name}", db_rep_res, suffix="table_pages")
app.add_route("/queries/top", db_rep_res, suffix="top_queries")


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, host="0.0.0.0", reload=True)
