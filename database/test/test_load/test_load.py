import json

from tinydb import Query

from database import load


def main():
    print(f"url = {load.YT_DATABASE_URL}")

    # Load data from url (uses YT_DATABASE_URL by default)
    db = load.from_url()

    # Get popular videos in trending table
    table = db.table("TRENDING")
    q = Query()
    result = table.search(q.viewCount > 5_000_000)
    print(f"Number of trending vids over 5M views: {len(result)}")


if __name__ == "__main__":
    main()
