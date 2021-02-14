import asyncio
import logging

import base64
from cryptography import fernet

from aiohttp import web
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from neoscrapers.const import SERVER_CONF

_LOGGER = logging.getLogger(__name__)

class NeoScraperServer:
    def __init__(
        self,
        host: str,
        port: int,
        app: web.Application = web.Application()
    ):
        """NeoScraperServer

        Args:
            host (str): server host address
            port (int): server port
            app (aiohttp.web.Application, optional): app to host. Defaults to web.Application().
        """
        self._host = host
        self._port = port
        self.app = app

    async def run(self) -> None:
        fernet_key = fernet.Fernet.generate_key()
        secret_key = base64.urlsafe_b64decode(fernet_key)
        setup(self.app, EncryptedCookieStorage(secret_key))

        runner = web.AppRunner(self.app)
        await runner.setup()

        site = web.TCPSite(runner, SERVER_CONF.HOST, SERVER_CONF.PORT)
        await site.start()

        _LOGGER.info(f"API server started on: http://{SERVER_CONF.HOST}:{SERVER_CONF.PORT}")

        _LOGGER.info(f"routes count: {len(self.app.router._resources)}")

        while True:
            await asyncio.sleep(3600)
