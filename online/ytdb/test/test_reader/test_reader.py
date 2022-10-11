import json

from ytdb.reader.reader import YouTubeReader

import pandas as pd


def main():
    # Create reader
    yt_reader = YouTubeReader()

    # Insert data
    with open("example_data/trending1.json") as file:
        t1 = json.load(file)

    path = "df_trending.xz"
    yt_reader.insert_videos(t1, path)

    # Queries ---------------------------------

    df = pd.read_pickle(path)


if __name__ == "__main__":
    main()
