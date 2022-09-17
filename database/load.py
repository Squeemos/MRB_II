"""Contains utility definitions for loading data from databases.
"""

from tinydb import TinyDB

from database.storage import OnlineJSONStorage

YT_DATABASE_URL = "https://squeemos.pythonanywhere.com/static/youtube.json"


def _docstring_parameter(*sub):
    """Decorator for inserting variables into function docstrings."""
    def dec(obj):
        obj.__doc__ = obj.__doc__.format(*sub)
        return obj
    return dec


@_docstring_parameter(YT_DATABASE_URL)
def from_url(data_url: str = YT_DATABASE_URL):
    """Convenience function for loading a TinyDB database from a web address.

    As of now, only supports loading databases in JSON format.

    Parameters
        data_url: Online address at which TinyDB data is retrievable.
            Defaults to YT_DATABASE_URL defined at top of 'database.load'.
            YT_DATABASE_URL = {0}
    """
    return TinyDB(data_url, storage=OnlineJSONStorage)
