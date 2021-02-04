"""Jumbo scraper"""
import logging

from neoscrapers.helpers.scraper import Scraper

_LOGGER = logging.getLogger(__name__)


def setup(manager):
    manager.register_scraper("jumbo", JumboScraper)


class JumboScraper(Scraper):
    def __init__(self):
        pass
