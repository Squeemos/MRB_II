"""Contains utility definitions for loading data from databases.
"""

from tinydb import TinyDB

from ytdb.storage import OnlineJSONStorage, OnlineBetterJSONStorage


YT_DATABASE_URL = "https://squeemos.pythonanywhere.com/static/youtube.json"


def from_url(data_url: str = YT_DATABASE_URL, storage: str = "default"):
    """Convenience function for loading a TinyDB ytdb from a web address.

    As of now, only supports loading databases in JSON format.

    Parameters
        data_url: Online address at which TinyDB data is retrievable.
            Defaults to YT_DATABASE_URL defined at top of 'ytdb.load'.
        storage: String indicating storage type hosted at data_url.
            Use "default" if normal JSON and "better" if BetterJSONStorage.
    """
    if storage == "default":
        return TinyDB(data_url, storage=OnlineJSONStorage)
    elif storage == "better":
        return TinyDB(data_url, storage=OnlineBetterJSONStorage)
