import os
import json
import string
from urllib.request import urlopen
import tinydb

class OnlineStorage(tinydb.Storage):
    def __init__(self, link):
        self.link = link

    def read(self):
        response = urlopen(self.link)
        data = json.loads(response.read())
        return data

    def write(self, data):
        pass

    def close(self):
        pass

if __name__ == '__main__':
    my_url = "https://squeemos.pythonanywhere.com/static/youtube.json"

    database = tinydb.TinyDB(my_url, storage = OnlineStorage)
    table = database.table("TRENDING")

    q = tinydb.Query()
    result = table.search(q.viewCount > 5_000_000)
    print(json.dumps(result, indent = 4))
