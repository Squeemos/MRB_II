import json
from urllib.request import urlopen

from tinydb import Storage, TinyDB, Query

from pathlib import Path
from BetterJSONStorage import BetterJSONStorage

from blosc2 import decompress
from orjson import loads


class OnlineBetterJSONStorage(Storage):
    def __init__(self, data_url: str):
        response = urlopen(data_url)
        self._db_bytes = response.read()

        self._data = self.load()

    def read(self):
        return self._data

    def write(self, data):
        raise NotImplementedError("Cannot update online JSON!")

    def load(self):
        if len(self._db_bytes):
            return loads(decompress(self._db_bytes))
        else:
            return None


def main():
    item1 = test_local(40)

    item2 = test_online(40)

    print(f"Items match? : {item1 == item2}")


def test_local(item_no):
    with TinyDB(Path("output/better.json"), storage=BetterJSONStorage) as db:
        table = db.table("TRENDING")

        q = Query()
        result = table.search(q.viewCount > 5_000_000)
        print(f"Number of trending vids over 5M views: {len(result)}")

        return json.dumps(table.all()[item_no], indent=4)


def test_online(item_no):
    url = "https://squeemos.pythonanywhere.com/static/better.json"

    with TinyDB(url, storage=OnlineBetterJSONStorage) as db:
        table = db.table("TRENDING")

        q = Query()
        result = table.search(q.viewCount > 5_000_000)
        print(f"Number of trending vids over 5M views: {len(result)}")

        return json.dumps(table.all()[item_no], indent=4)




if __name__ == "__main__":
    main()
