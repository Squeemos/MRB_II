import os
import json
from datetime import datetime

import tinydb
from tinydb import TinyDB, Query

from youtube_reader import YouTubeReader


def main():
    # Create database
    db = TinyDB("db_trending.json", indent=2)
    db.truncate()

    # Create table
    table = db.table("MEGATABLE")
    table.truncate()

    # Create reader
    yt_reader = YouTubeReader()

    # Insert data
    yt_reader.insert_videos("example_data/trending1.json", table)
    # yt_reader.insert_videos(table, "example_data/trending2.json")

    # Queries ---------------------------------

    # Print one video
    vid = get_vids_by_title(table, "Nintendo Direct 9.13.2022")
    pprint(vid)

    dt = datetime.strptime(vid["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
    print(dt)


def pprint(data):
    print(json.dumps(data, indent=2))


def get_vids_by_title(table, title):
    query = Query()
    vids = table.search(query.title == title)

    if len(vids) == 1:
        return vids[0]

    return vids


if __name__ == "__main__":
    main()
