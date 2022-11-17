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

    drop_substrings = (
        "localization",
    )

    # Constructor --------------------------------------------------------------

    def __init__(self, time: str = None):
        if time is None:
            time = datetime.now(timezone("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")

        self.time = time

    # Video Data ---------------------------------------------------------------

    def insert_videos(self, data: dict, path: str, last_month: bool = True):
        """Inserts client response data as dict into dataframe at given path.

        Several fields are encoded according to their datatype (datetimes,
        integers, booleans, ...)

        Parameters:
            data: YT API response as a dictionary
            path: Path to either existing or new dataframe file
            last_month: Whether to drop all data over a month
        """
        # Attempt to load dataframe from given path
        try:
            df = pd.read_feather(path)
        except FileNotFoundError:
            df = pd.DataFrame()

        # Create data frame from individual entries
        df_new = self.videos_to_df(data)

        # Insert new entries into the table
        df = pd.concat(
            [df, df_new], ignore_index=True, sort=False
        )

        # Convert datetimes
        for dt_feat in YouTubeReader.dt_names:
            df[dt_feat] = pd.to_datetime(df[dt_feat], utc=True)

        # Get only last month
        if last_month:
            df = self.last_month(df)

        # Pickle dict
        df.to_feather(path, compression="zstd")

    def videos_to_df(self, data: dict):
        """Takes a response for videos and returns a dataframe.

        Parameters:
            data: YT API response with category video data as a dictionary.
        """
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

        df = pd.DataFrame(entries)

        # Drop all features containing substrings
        df = df.loc[:, [col for col in df.columns if not any(d in col for d in YouTubeReader.drop_substrings)]]

        return pd.DataFrame(entries)

    @staticmethod
    def last_month(df: pd.DataFrame, time_feature_name: str = "queryTime"):
        """Returns only last month of given data based on the given feature.

        Parameters
            df: DataFrame to reduce to only last month's data
            time_feature_name: Name of time feature to use to
        """
        return df.set_index(time_feature_name).last("30D").reset_index()

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
