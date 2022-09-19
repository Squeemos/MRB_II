import tinydb
import json

from ytdb.storage import OnlineJSONStorage

def main():
    my_url = "https://squeemos.pythonanywhere.com/static/youtube.json"

    database = tinydb.TinyDB(my_url, storage = OnlineJSONStorage)
    table = database.table("TRENDING")

    q = tinydb.Query()
    result = table.search(q.viewCount > 5_000_000)
    print(json.dumps(result, indent = 4))

if __name__ == '__main__':
    main()
