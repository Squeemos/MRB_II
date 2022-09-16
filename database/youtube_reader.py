"""Contains YouTubeReader class that inserts YTD API data in TinyDB formats.
"""

from typing import Union

import json

from datetime import datetime
from pytz import timezone

from tinydb import TinyDB
from tinydb.table import Table


class YouTubeReader:
    """Reader for inserting YouTube Data API responses into TinyDB formats.
    """

    # Features to Encode -------------------------------------------------------

    int_names = (
        "categoryId",
        "viewCount",
        "likeCount",
        "favoriteCount",
        "commentCount",
    )

    # Video Data ---------------------------------------------------------------

    def insert_videos(self, data: Union[str, dict], table: Union[TinyDB, Table]):
        """Inserts video data into the given database or table.

        Each video in the given API query result is inserted separately into
        the given table as a new sample.

        Each inserted sample is given a UTC timestamp. Additionally, each of
        the query 'parts' (i.e. 'statistics', 'snippet') are flattened. Some
        fields' data type are converted for easier TinyDB querying.

        Parameters:
            data: YT API response JSON either as filepath or loaded dict
            table: TinyDB database or table which supports insertion
        """
        # If filepath given, convert .json at location to dict
        if isinstance(data, str):
            with open(data, "r") as file:
                data = json.load(file)

        # Create time string from current UTC time and f
        dt = datetime.now(timezone("UTC"))
        time = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        timestamp = dt.timestamp()

        # Insert each video individually
        for item in data["items"]:
            item = self._flatten_dict(item)

            # Add time data to video
            entry = {"time": time, "timestamp": timestamp}
            entry.update(item)

            # Convert fields prior to insertion
            self._encode_fields(entry)

            # Insert into the table
            table.insert(entry)

    @staticmethod
    def _encode_fields(entry: dict):
        # Integer fields
        for int_name in YouTubeReader.int_names:
            try:
                entry[int_name] = int(entry[int_name])
            except (KeyError, ValueError):
                pass

        return entry

    # Helpers ------------------------------------------------------------------

    @staticmethod
    def _flatten_dict(data: dict):
        """Flattens first level of dictionary."""
        flat = dict()

        for k1, v1 in data.items():
            if isinstance(v1, dict):
                for k2, v2 in v1.items():
                    flat[k2] = v2
            else:
                flat[k1] = v1

        return flat
