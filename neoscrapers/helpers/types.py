from abc import ABC
from typing import Optional, Any

from selenium.webdriver.remote.webdriver import WebDriver
from neoscrapers.helpers.util import Observable


class Scraper(ABC):
    selenium_driver: Optional[WebDriver] = None

    @property
    def name(self) -> str:
        return ""

    @property
    def progress(self) -> Observable:
        return None

    @property
    def output(self):
        return None

    async def run(self, **kwargs: Any):
        raise NotImplementedError()
