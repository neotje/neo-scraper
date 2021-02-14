
"""
ScraperManager: done
NeoScrapers: done
Scraper: done
sessions: done
OutputManager: done
UserManager: done
"""

from neoscrapers.users import UserManager
from neoscrapers import data
from neoscrapers.output import OutputManager
from neoscrapers.scrapermanager import NeoScraperManager
from neoscrapers.routes import setup_routes
from neoscrapers.server import NeoScraperServer
from .const import SERVER_CONF
import asyncio
import logging
import sys

from aiohttp import web


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(funcName)s:[%(lineno)d]   %(message)s'
)
_LOGGER = logging.getLogger(__name__)


def run():
    _LOGGER.info("Starting NeoScrapers.")

    try:
        asyncio.run(async_run())
    except KeyboardInterrupt:
        pass
    finally:
        stop()


server = NeoScraperServer(SERVER_CONF.HOST, SERVER_CONF.PORT)
scraper_manager = NeoScraperManager()
output_manager = OutputManager()
user_manager = UserManager()


async def async_run():
    """
    start neoscraper
    """
    await scraper_manager.setup()

    setup_routes(server.app)

    await server.run()


def stop():
    data.save()