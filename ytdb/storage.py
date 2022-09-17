"""Contains custom TinyDB storage definitions.
"""

import json
from urllib.request import urlopen

from tinydb import Storage


class OnlineJSONStorage(Storage):
    """Storage for opening and reading TinyDB databases hosted online.

    Parameters:
        data_url: Online address at which TinyDB data is retrievable.

    Attributes:
        data_url: Saved data address.
    """
    def __init__(self, data_url: str):
        self.data_url = data_url

    def read(self):
        response = urlopen(self.data_url)
        data = json.loads(response.read())
        return data

    def write(self, data):
        raise NotImplementedError("Cannot update online JSON!")
