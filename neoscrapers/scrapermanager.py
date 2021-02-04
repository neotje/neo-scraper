import logging
import pathlib
import importlib
import json
from types import ModuleType
from typing import TypedDict

from neoscrapers.helpers.scraper import Scraper

_LOGGER = logging.getLogger(__name__)


class NeoScraperManager:
    def __init__(self):
        self.ouput_manager = None
        self._cache = {}
        self.scrapers = {}

    def setup(self):
        integrations = get_integrations(self)

        for intergration in integrations:
            component = intergration.get_component()

            if hasattr(component, "setup"):
                component.setup(self)

    def register_scraper(self, name: str, scraper: Scraper):
        self.scrapers[name] = scraper


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


def get_integrations(manager: NeoScraperManager):
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
