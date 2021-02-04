import logging
import sys

from aiohttp import web

from .const import SERVER_CONF
from neoscrapers.server import NeoScraperServer
from neoscrapers.scrapermanager import NeoScraperManager
from neoscrapers.output import OutputManager

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(funcName)s:[%(lineno)d]   %(message)s'
)
_LOGGER = logging.getLogger(__name__)


def run():
    _LOGGER.info("Starting NeoScrapers.")

    neoscraper = NeoScraper()

    try:
        neoscraper.run()
    except KeyboardInterrupt:
        pass
    finally:
        neoscraper.stop()


class NeoScraper:
    def __init__(self):
        self.app = web.Application()

        self.server = NeoScraperServer(SERVER_CONF.HOST, SERVER_CONF.PORT)
        self.scraper_manager = NeoScraperManager()
        self.output_manager = OutputManager()

    def run(self):
        self.scraper_manager.setup()
        self.server.run()

    def stop(self):
        pass
