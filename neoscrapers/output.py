import logging
import pathlib
import random
from neoscrapers import outputfiles

_LOGGER = logging.getLogger(__name__)


class OutputManager:
    def __init__(self):
        self.output_root = pathlib.Path(outputfiles.__path__[0])

        _LOGGER.info(f"Output manager set to: {self.output_root}")

    def get_output(self, name: str, extension: str):
        name = f"{name}_{random.random()}"


class Output:
    def __init__(self, path: pathlib.Path, filename: str, ext: str):
        self.path = path
        self.file = f"{filename}.{ext}"

    @property
    def output_path(self) -> pathlib.Path:
        return self.path / self.file

    def open(self, mode: str = 'w'):
        if self._open is not None and self._open.mode == mode:
            return self._open

        self._open = open(mode)
        return self._open

    def close(self):
        self._open.close()
