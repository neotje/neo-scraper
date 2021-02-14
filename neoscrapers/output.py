import logging
import pathlib
import random
from typing import IO
from neoscrapers import outputfiles

_LOGGER = logging.getLogger(__name__)


class OutputManager:
    output_root = pathlib.Path(outputfiles.__path__[0])

    @classmethod
    def get_output(self, name: str, extension: str):
        """Get new unique output file.

        Args:
            name (str): file name
            extension (str): file extension

        Returns:
            neoscrapers.output.Ouput: unique output file
        """
        name = f"{name}_{random.random()}"

        return Output(self.output_root, name, extension)


class Output:
    def __init__(self, path: pathlib.Path, filename: str, ext: str):
        """Output

        Args:
            path (pathlib.Path): root folder path
            filename (str): file name
            ext (str): file extension
        """
        self.path = path
        self.file = f"{filename}.{ext}"
        self._open = None

    @property
    def output_path(self) -> pathlib.Path:
        """get output as pathlib.Path object

        Returns:
            pathlib.Path: output_path
        """
        return self.path / self.file

    def open(self, mode: str = 'w') -> IO[any]:
        """get IO instance of Output file

        Args:
            mode (str, optional): file mode. Defaults to 'w'.

        Returns:
            IO[any]: resulting file IO object
        """
        if self._open is not None and self._open.mode == mode:
            return self._open

        self._open = self.output_path.open(mode)
        return self._open

    def close(self):
        self._open.close()
