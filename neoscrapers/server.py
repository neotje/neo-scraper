import logging

from aiohttp import web
_LOGGER = logging.getLogger(__name__)


class NeoScraperServer:
    def __init__(
        self,
        host: None,
        port: int
    ):
        self._host = host
        self._port = port
        self.app = web.Application()

    def run(self) -> None:
        web.run_app(self.app)