# pylint: disable=missing-module-docstring
import decimal
import json
import logging
from dataclasses import asdict, is_dataclass
from functools import partial

import falcon
import falcon.asgi
import uvicorn
from dependency_injector.wiring import Provide, inject
from falcon import media

from db_report.containers.containers import Container
from db_report.storage.db import DbConnection, NotFoundError


class DataClassSerializer(json.JSONEncoder):
    """Custom serializer for Falcon API that handles non-standard python types"""

    def default(self, o):  # type: ignore[no-untyped-def]
        if is_dataclass(o):
            return asdict(o)  # type: ignore[arg-type]
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super().default(o)


dataclasses_json_serializer = media.JSONHandler(
    dumps=partial(json.dumps, cls=DataClassSerializer),
)
extra_handlers = {"application/json": dataclasses_json_serializer}


class DbReportResource:
    """Main entrypoint for fetching DB stats resources"""

    def __init__(self) -> None:
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @inject
    async def on_get_table_pages(
        self,
        req: falcon.asgi.request.Request,  # pylint: disable=unused-argument
        resp: falcon.asgi.response.Response,
        table_name: str,
        db_connection: DbConnection = Provide[Container.db_connection],
    ) -> None:
        """
        Method for fetching data on table pages density from DB repo
        """
        self._logger.info("Called for pages for table %s", table_name)
        try:
            data = await db_connection.get_table_pages(table_name)
        except NotFoundError as e:
            self._logger.error("%s", e)
            resp.status = falcon.HTTP_404
            resp.content_type = falcon.MEDIA_TEXT
            resp.text = f"Could not access table {table_name}!"
        else:
            resp.status = falcon.HTTP_200
            resp.content_type = falcon.MEDIA_JSON
            resp.media = data

    @inject
    async def on_get_top_queries(
        self,
        req: falcon.asgi.request.Request,  # pylint: disable=[unused-argument]
        resp: falcon.asgi.response.Response,
        db_connection: DbConnection = Provide[Container.db_connection],
    ) -> None:
        """
        Method for fetching top most used queries in DB
        """
        try:
            data = await db_connection.get_top_queries()
        except NotFoundError as e:
            self._logger.error("%s", e)
            resp.status = falcon.HTTP_404
            resp.content_type = falcon.MEDIA_TEXT
            resp.text = "Could not access data!"
        else:
            resp.status = falcon.HTTP_200
            resp.content_type = falcon.MEDIA_JSON
            resp.media = data


container = Container()
container.logging.init()
container.wire(modules=[__name__])

app = falcon.asgi.App()
app.resp_options.media_handlers.update(extra_handlers)
db_rep_res = DbReportResource()
app.add_route("/page/{table_name}", db_rep_res, suffix="table_pages")
app.add_route("/queries/top", db_rep_res, suffix="top_queries")


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, host="0.0.0.0", reload=True)
