import logging

import asyncio
import pathlib
import yaml

from neoscrapers import helpers

_LOGGER = logging.getLogger(__name__)

_cache = None
work_queue = asyncio.Queue()

config_path = pathlib.Path(helpers.__path__[0]) / "config.yaml"
config_file = open(config_path, 'r')
config_dict = yaml.full_load(config_file)

_LOGGER.info(f"Loading config: {config_path}")

if config_dict is None:
    config_dict = {}

_LOGGER.info(config_dict)

def save():
    with open(config_path, 'w') as file:
        yaml.dump(config_dict, file)
