from abc import ABC
from typing import Optional, Any

from selenium.webdriver.remote.webdriver import WebDriver


class Scraper(ABC):
    neoscraper: Optional["NeoScraper"] = None

    selenium_driver: Optional[WebDriver] = None

    @property
    def name(self) -> Optional[str]:
        return None

    @property
    def progress(self) -> int:
        return 0

    @property
    def output(self):
        return None

    async def async_run(self, **kwargs: Any):
        raise NotImplementedError()
