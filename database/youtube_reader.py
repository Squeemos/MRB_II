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

    bool_names = (
        "caption",
        "licensedContent",
        "embeddable",
        "publicStatsViewable",
        "madeForKids",
    )

    dt_names = (
        "publishedAt",
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
            entry = {"queryTime": time, "queryTimestamp": timestamp}
            entry.update(item)

            # Convert fields prior to insertion
            self._encode_fields(entry)

            # Insert into the table
            table.insert(entry)

    @staticmethod
    def _encode_fields(entry: dict):
        """Encodes some integer, boolean, datetime fields

        Parameters
            entry: Individual video entry to be inserted in table.
        """
        # Integer fields
        for int_name in YouTubeReader.int_names:
            try:
                entry[int_name] = int(entry[int_name])
            except (KeyError, ValueError):
                pass

        # Boolean fields
        for bool_name in YouTubeReader.bool_names:
            try:
                if isinstance(entry[bool_name], str):
                    entry[bool_name] = bool(entry[bool_name])
            except (KeyError, ValueError):
                pass

        # Datetime fields
        for dt_name in YouTubeReader.dt_names:
            try:
                ts = datetime.strptime(entry[dt_name], "%Y-%m-%dT%H:%M:%SZ").timestamp()
                entry[f"{dt_name}Timestamp"] = ts
            except (KeyError, TypeError):
                pass

        return entry

    # Helpers ------------------------------------------------------------------

    @staticmethod
    def _flatten_dict(data: dict):
        """Flattens first level of dictionary."""
        flat = dict()

        # For items in orignal json
        for k1, v1 in data.items():
            if isinstance(v1, dict):
                # For items in part (ie snippet)
                for k2, v2 in v1.items():
                    # ex. title, description
                    flat[k2] = v2
            else:
                # ex. kind, etag, id
                flat[k1] = v1

        return flat
