"""Contains YouTubeReader that inserts YTD API data into Pandas DataFrames."""

from datetime import datetime
from pytz import timezone

import pandas as pd


class YouTubeReader:
    """Reader for inserting YouTube Data API responses into Pandas DataFrames.

    The DataFrames being created or updated must be feathered .feather files.
    """

    # Features to Encode -------------------------------------------------------

    int_names = (
        "snippet.categoryId",
        "statistics.viewCount",
        "statistics.likeCount",
        "statistics.favoriteCount",
        "statistics.commentCount",
    )

    bool_names = (
        "contentDetails.caption",
        "contentDetails.licensedContent",
        "status.embeddable",
        "status.publicStatsViewable",
        "status.madeForKids",
    )

    dt_names = (
        "queryTime",
        "snippet.publishedAt",
    )

    # Constructor --------------------------------------------------------------

    def __init__(self, time: str = None):
        if time is None:
            time = datetime.now(timezone("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")

        self.time = time

    # Video Data ---------------------------------------------------------------

    def insert_videos(self, data: dict, path: str):
        """Inserts video data into the pickled df (.xz) at the given path.

        Several fields are encoded according to their datatype (datetimes,
        integers, booleans, ...)

        Parameters:
            data: YT API response as a dictionary.
            path: Path to either existing or new feathered dataframe file (.feather)
        """
        # Attempt to load dataframe from given path
        try:
            df = pd.read_feather(path)
        except FileNotFoundError:
            df = pd.DataFrame()

        # Create individual entries
        entries = []
        for item in data["items"]:
            item = self._flatten_dict(item)

            # Add time data to video
            entry = {"queryTime": self.time}
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
            df[dt_feat] = pd.to_datetime(df[dt_feat], utc=True)

        # Pickle dict
        df.to_feather(path, compression = "zstd")

    def insert_categories(self, data : dict, df : pd.DataFrame):
        # Create individual entries
        entries = []
        for item in data["items"]:
            item = self._flatten_dict(item)

            # Add time data to video
            entry = {"queryTime": self.time}
            entry.update(item)

            # Convert fields prior to insertion
            self._encode_fields(entry)

            entries.append(entry)

        # Combine the data and the current dataframe
        df = pd.concat([df, pd.DataFrame(entries)], ignore_index = True, sort = False)

        # Convert datetimes
        for dt_feat in YouTubeReader.dt_names:
            df[dt_feat] = pd.to_datetime(df[dt_feat], utc=True)


        return df

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
        flat = list(pd.json_normalize(data).T.to_dict().values())[0]

        return flat
