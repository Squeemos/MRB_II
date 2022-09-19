"""Moves online data into normal and better JSON storages for size comparison.
"""

from tinydb import TinyDB

from pathlib import Path
from BetterJSONStorage import BetterJSONStorage

from ytdb import load


def main():
    # Load data from url
    db = load.from_url()

    # Get popular videos in trending table
    table = db.table("TRENDING")

    all_entries = table.all()

    with TinyDB("output/normal.json") as db_n:
        table_n = db_n.table("TRENDING")
        table_n.truncate()

        for entry in all_entries:
            table_n.insert(entry)

    with TinyDB(Path("output/better.json"), access_mode="r+", storage=BetterJSONStorage) as db_b:
        table_b = db_b.table("TRENDING")
        table_b.truncate()

        for entry in all_entries:
            table_b.insert(entry)

    db.close()


if __name__ == "__main__":
    main()
