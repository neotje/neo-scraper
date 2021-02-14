import asyncio
import logging
import pathlib
import importlib
import json
from types import ModuleType
from typing import TypedDict

from neoscrapers.helpers.types import Scraper

_LOGGER = logging.getLogger(__name__)


class NeoScraperManager:
    def __init__(self):
        self._cache = {}
        self.scrapers = {}

    async def setup(self):
        integrations = await get_integrations(self)

        await asyncio.gather(
            *(
                intergration.get_component().setup(self)
                for intergration in integrations
                if hasattr(intergration.get_component(), "setup")
            )
        )

    async def register_scraper(self, name: str, scraper: Scraper):
        """add scraper to dictonary

        Args:
            name (str): scraper name
            scraper (neoscrapers.helpers.scraper.Scraper): Scraper object
        """
        self.scrapers[name] = scraper

    def scraper_names(self):
        """tuple with scraper names

        Returns:
            tuple: list of scraper names
        """
        return (s.name for s in self.scrapers)


class Manifest(TypedDict, total=False):
    name: str
    domain: str


class Integration:

    @classmethod
    def resolve_from_root(
        cls,
        manager: NeoScraperManager,
        module: ModuleType,
        domain: str
    ):
        """[summary]

        Args:
            manager (neoscrapers.scrapermanager.NeoScraperManager): scrapermanager for cache.
            module (types.ModuleType): module
            domain (str): domain name

        Returns:
            neoscrapers.scrapermanager.Integration: Integration
        """
        for base in module.__path__:
            manifest_path = pathlib.Path(base) / domain / "manifest.json"

            if not manifest_path.is_file():
                continue

            try:
                _LOGGER.debug(f"{domain} manifest path {manifest_path}")
                manifest = json.loads(manifest_path.read_text())
            except ValueError as err:
                _LOGGER.error(
                    f"Error parsing manifest.json file at {manifest_path}: {err}"
                )
                continue

            return cls(
                manager,
                f"{module.__name__}.{domain}",
                manifest_path.parent,
                manifest
            )

        return None

    def __init__(
        self,
        manager: NeoScraperManager,
        pkg_path: str,
        file_path: pathlib.Path,
        manifest: Manifest
    ):
        """Integration

        Args:
            manager (neoscrapers.neoscrapermanager.NeoScraperManager): for cache purposes
            pkg_path (str): pkg path to module
            file_path (pathlib.Path): file path to module
            manifest (neoscraper.neoscrapermanager.Manifest): Manifest
        """
        self.manager = manager
        self.pkg_path = pkg_path
        self.file_path = file_path
        self.manifest = manifest

        _LOGGER.info(f"Loaded {self.name} from {self.pkg_path}")

    @property
    def name(self) -> str:
        return self.manifest["name"]

    @property
    def domain(self) -> str:
        return self.manifest["domain"]

    def get_component(self) -> ModuleType:
        if self.domain not in self.manager._cache:
            _LOGGER.debug(
                f"Storing {self.name} from {self.pkg_path} to ScraperManager cache.")
            self.manager._cache[self.domain] = importlib.import_module(
                self.pkg_path)
        return self.manager._cache[self.domain]


async def get_integrations(manager: NeoScraperManager):
    from neoscrapers import scrapers

    dirs = (
        entry
        for path in scrapers.__path__
        for entry in pathlib.Path(path).iterdir()
        if entry.is_dir()
    )

    integrations = (
        Integration.resolve_from_root(manager, scrapers, comp.name)
        for comp in dirs
    )

    return integrations
