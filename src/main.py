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

from src.db_report.containers.containers import Container
from src.db_report.core.core_api import DBStats
from src.db_report.storage.db import NotFoundError


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

    @inject
    def __init__(self, core_api: DBStats = Provide[Container.core_api]) -> None:
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._core_api = core_api

    async def on_get_table_pages(
        self,
        req: falcon.asgi.request.Request,  # pylint: disable=unused-argument
        resp: falcon.asgi.response.Response,
        table_name: str,
    ) -> None:
        """
        Method for fetching data on table pages density from DB repo
        """
        self._logger.info("Called for pages for table %s", table_name)
        try:
            data = await self._core_api.get_table_pages(table_name)
        except NotFoundError as e:
            self._logger.error("%s", e)
            resp.status = falcon.HTTP_404
            resp.content_type = falcon.MEDIA_TEXT
            resp.text = f"Could not access table {table_name}!"
        else:
            resp.status = falcon.HTTP_200
            resp.content_type = falcon.MEDIA_JSON
            resp.media = data

    async def on_get_top_queries(
        self,
        req: falcon.asgi.request.Request,  # pylint: disable=[unused-argument]
        resp: falcon.asgi.response.Response,
    ) -> None:
        """
        Method for fetching top most used queries in DB
        """
        try:
            data = await self._core_api.get_top_queries()
        except NotFoundError as e:
            self._logger.error("%s", e)
            resp.status = falcon.HTTP_404
            resp.content_type = falcon.MEDIA_TEXT
            resp.text = "Could not access data!"
        else:
            resp.status = falcon.HTTP_200
            resp.content_type = falcon.MEDIA_JSON
            resp.media = data

    async def on_get_top_tables(
        self,
        req: falcon.asgi.request.Request,  # pylint: disable=[unused-argument]
        resp: falcon.asgi.response.Response,
    ) -> None:
        """
        Method for fetching top tables in size in DB
        """
        try:
            data = await self._core_api.get_top_table_sizes()
        except NotFoundError as e:
            self._logger.error("%s", e)
            resp.status = falcon.HTTP_404
            resp.content_type = falcon.MEDIA_TEXT
            resp.text = "Could not access data!"
        else:
            resp.status = falcon.HTTP_200
            resp.content_type = falcon.MEDIA_JSON
            resp.media = data

    async def on_get_dead_tuples(
        self,
        req: falcon.asgi.request.Request,  # pylint: disable=[unused-argument]
        resp: falcon.asgi.response.Response,
    ) -> None:
        """
        Method for fetching top tables in size in DB
        """
        try:
            data = await self._core_api.get_dead_tuples()
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
app.add_route("/tables/top", db_rep_res, suffix="top_tables")
app.add_route("/dead-tuples", db_rep_res, suffix="dead_tuples")


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, host="0.0.0.0", reload=True)
