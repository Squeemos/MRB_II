import json
from datetime import datetime

from tinydb import TinyDB, Query

from ytdb.reader import YouTubeReader

def main():
    # Create ytdb
    db = TinyDB("db_trending.json", indent=2)
    db.truncate()

    # Create table
    table = db.table("MEGATABLE")
    table.truncate()

    # Create reader
    yt_reader = YouTubeReader()

    # Insert data
    with open("example_data/trending1.json") as file:
        t1 = json.load(file)
    yt_reader.insert_videos(t1, table)
    yt_reader.insert_videos("example_data/trending2.json", table)

    # Queries ---------------------------------

    # Print one video
    vid = get_vids_by_title(table, "Nintendo Direct 9.13.2022")
    pprint(vid)

    # Get video from date range
    Published = Query()
    vids = table.search(
        (Published.publishedAtTimestamp > datetime(2022, 9, 12).timestamp())
        &
        (Published.publishedAtTimestamp < datetime(2022, 9, 14).timestamp())
    )
    pprint(vids)
    print(len(vids))

    with open("query_result.json", "w") as outfile:
        json.dump(vids, outfile, indent=4)


def pprint(data):
    print(json.dumps(data, indent=2))


def get_vids_by_title(table, title):
    Vids = Query()
    vids = table.search(Vids.title == title)

    if len(vids) == 1:
        return vids[0]

    return vids


if __name__ == "__main__":
    main()
