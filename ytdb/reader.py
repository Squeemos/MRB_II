"""Contains YouTubeReader that inserts YTD API data into Pandas DataFrames.
"""

from datetime import datetime
from pytz import timezone

import pandas as pd


class YouTubeReader:
    """Reader for inserting YouTube Data API responses into Pandas DataFrames.

    The DataFrames being created or updated must be pickled .xz files.
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
        "queryTime",
        "publishedAt",
    )

    # Video Data ---------------------------------------------------------------

    def insert_videos(self, data: dict, path: str):
        """Inserts video data into the pickled df (.xz) at the given path.

        Several fields are encoded according to their datatype (datetimes,
        integers, booleans, ...)

        Parameters:
            data: YT API response as a dictionary.
            path: Path to either existing or new pickled dataframe file (.xz)
        """
        # Attempt to load dataframe from given path
        try:
            df = pd.read_pickle(path)
        except FileNotFoundError:
            df = pd.DataFrame()

        # Create time string from current UTC time and f
        dt = datetime.now(timezone("UTC"))
        time = dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Create individual entries
        entries = []
        for item in data["items"]:
            item = self._flatten_dict(item)

            # Add time data to video
            entry = {"queryTime": time}
            entry.update(item)

            # Convert fields prior to insertion
            self._encode_fields(entry)

            entries.append(entry)

        # Insert new entries into the table
        df_new = pd.DataFrame(entries)
        df = pd.concat(
            [df, df_new], ignore_index=True, sort=False
        )

        # Convert datetimes
        for dt_feat in YouTubeReader.dt_names:
            df[dt_feat] = pd.to_datetime(df[dt_feat])

        # Pickle dict
        pd.to_pickle(
            df, path, compression={"method": "xz"}, protocol=-1
        )

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
                    if k2 not in flat:
                        flat[k2] = v2
            else:
                # ex. kind, etag, id
                flat[k1] = v1

        return flat
