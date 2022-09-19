"""Contains custom TinyDB storage definitions.

Contains storage classes that allow the loading of TinyDB databases that
are hosted online with both default and BetterJSONStorage storages. These
are necessarily read-only.
"""

import json
from urllib.request import urlopen

from tinydb import Storage

from blosc2 import decompress
from orjson import loads


class OnlineJSONStorage(Storage):
    """Storage for opening and reading TinyDB databases hosted online.

    Parameters:
        data_url: Online address at which TinyDB data is retrievable.
    """
    def __init__(self, data_url: str):
        response = urlopen(data_url)
        self._db_bytes = response.read()
        self._data = self._load()

    def read(self):
        return self._data

    def write(self, data):
        raise NotImplementedError("Cannot update online JSON!")

    def _load(self):
        if len(self._db_bytes):
            return json.loads(self._db_bytes)
        else:
            return None


class OnlineBetterJSONStorage(Storage):
    """Storage for opening online TinyDB databases using BetterJSONStorage.

    Parameters:
        data_url: Online address at which TinyDB data is retrievable.
    """
    def __init__(self, data_url: str):
        response = urlopen(data_url)
        self._db_bytes = response.read()

        self._data = self._load()

    def read(self):
        return self._data

    def write(self, data):
        raise NotImplementedError("Cannot update online JSON!")

    def _load(self):
        if len(self._db_bytes):
            return loads(decompress(self._db_bytes))
        else:
            return None
