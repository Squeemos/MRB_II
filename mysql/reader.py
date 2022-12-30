"""Contains YouTubeReader that inserts YTD API data into MySQL Database."""

from datetime import datetime
from pytz import timezone

import pandas as pd

import sqlalchemy as sqa


class YouTubeReader:
    """Reader for inserting YouTube Data API responses into database.
    """
    # Table Schemas --------------------------------------------------------------------------

    video_schema = {
        "queryNum": sqa.Integer,
        "queryTime": sqa.DateTime,

        "id": sqa.Text,
        
        "snippet.categoryId": sqa.Integer,
        "snippet.publishedAt": sqa.DateTime,
        "snippet.channelId": sqa.Text,
        "snippet.title": sqa.Text,
        "snippet.description": sqa.Text,
        "snippet.channelTitle": sqa.Text,
        
        "statistics.viewCount": sqa.BigInteger,
        "statistics.likeCount": sqa.BigInteger,
        "statistics.commentCount": sqa.BigInteger,

        "contentDetails.duration": sqa.BigInteger, 
    }

    tag_schema = {
        "queryNum": sqa.Integer,

        "id": sqa.Text,
        
        "snippet.tags": sqa.Text, 
    }

    thumbnail_schema = {
        "queryNum": sqa.Integer,

        "id": sqa.Text,
        
        "default.url": sqa.Text,
        "default.width": sqa.Integer,
        "default.height": sqa.Integer,

        "medium.url": sqa.Text,
        "medium.width": sqa.Integer,
        "medium.height": sqa.Integer,

        "high.url": sqa.Text,
        "high.width": sqa.Integer,
        "high.height": sqa.Integer,

        "standard.url": sqa.Text,
        "standard.width": sqa.Integer,
        "standard.height": sqa.Integer,

        "maxres.url": sqa.Text,
        "maxres.width": sqa.Integer,
        "maxres.height": sqa.Integer,
    }

    # Constructor/Destructor----------------------------------------------------

    def __init__(self, username: str, key: str, hostname: str, dbname: str,
                 query_num_table_name: str):
        """Initializes the reader with a database engine and consistent query info.

        Params:
            username: Database user name
            key: Database pwd associated w/ user
            hostname: Database host name (ex. localhost)
            dbname: Database name (ex. trending)
            query_num_table_name: Name of table to check when determining query no.
        """
        # Create engine
        #   engine = create_engine("mysql://user:pwd@host/db_name", echo=True)
        #connect_str = f"mysql+mysqlconnector://{username}:{key}@{hostname}/{dbname}"  # online
        connect_str = f"mysql://{username}:{key}@{hostname}/{dbname}"                  # local
        self.engine = sqa.create_engine(connect_str, pool_recycle=280, echo=False)

        # Save query information
        self.query_number = self._get_query_number(self.engine, query_num_table_name)
        self.query_time = datetime.now(timezone("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Video Data ---------------------------------------------------------------

    def insert_videos(self, data: dict):
        # Read client response into flattened dataframe
        df = pd.json_normalize(data["items"], max_level=1)

        # Save query specific features
        df["queryNum"] = self.query_number
        df["queryTime"] = self.query_time

        # Perform insertions
        self._insert_vids(df)
        self._insert_tags(df)
        self._insert_thumbnails(df)

    def _insert_vids(self, df):
        #self.engine.execute("DROP TABLE IF EXISTS videos")
        self._create_table("videos", self.video_schema)

        # Get only features that matter
        df_vid = df.loc[:, list(self.video_schema.keys())]

        # Convert duration to raw seconds
        df_vid["contentDetails.duration"] = pd.to_timedelta(
            df_vid["contentDetails.duration"].str.slice(start=2).str.replace("M", "m")
        ).dt.seconds

        # Convert columns to datetime
        dt_names = (
            "queryTime",
            "snippet.publishedAt",
        )
        for dt_feat in dt_names:
            df_vid[dt_feat] = pd.to_datetime(df_vid[dt_feat], utc=True)

        # Insert into database
        df_vid.to_sql("videos", self.engine, index=False, if_exists="append",
                      dtype=self.video_schema)

        return df

    def _insert_tags(self, df):
        self._create_table("tags", self.tag_schema)

        # Create tags dataframe
        df_tags = df.loc[:, ["id", "snippet.tags"]]
        df_tags = df_tags.explode("snippet.tags")
        df_tags["queryNum"] = self.query_number

        # Insert into database
        df_tags.to_sql("tags", self.engine, index=False, if_exists="append",
                       dtype=self.tag_schema)

    def _insert_thumbnails(self, df):
        self._create_table("thumbnails", self.thumbnail_schema)

        # Get thumbnail data
        df_thumb = pd.json_normalize(df["snippet.thumbnails"])
        df_thumb["queryNum"] = self.query_number

        # Get id from thumbnail name
        df_thumb["id"] = df_thumb["default.url"].str.split("/").apply(lambda x: x[-2])

        df_thumb.to_sql("thumbnails", self.engine, index=False, if_exists="append",
                        dtype=self.thumbnail_schema)


    # Helpers ------------------------------------------------------------------

    @staticmethod
    def _get_query_number(engine: sqa.engine.base.Engine, table_name: str,
                          query_feat_name: str = "queryNum"):
        try:
            query_number = pd.read_sql(f"SELECT MAX({query_feat_name}) FROM {table_name};", engine)
            query_number = query_number.iloc[0][0]
            query_number = query_number + 1 if query_number is not None else 1
        except:
            query_number = 1

        return query_number

    def _create_table(self, name: str, features: dict):
        """Given a name and a dictionary of features, creates and returns a table with SQLAlchemy.

        Params:
            name: Name of resulting table
            features: Dictionary of feature names as keys and SQLAlchemy data types as values
        """
        meta = sqa.MetaData()

        table = sqa.Table(
            name, meta,
            sqa.Column("num", sqa.Integer, primary_key=True),
            sqa.Column("queryNum", sqa.Integer, index=True),
            *[sqa.Column(name, dtype) for name, dtype in features.items()],
        )

        meta.create_all(self.engine)

        return table
