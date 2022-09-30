import tinydb
import datetime
from matplotlib import pyplot as plt
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import json
import numpy as np

import time
from tqdm import tqdm

# Local imports
from ytdb.storage import OnlineBetterJSONStorage

def function_timer(f):
    def inner(*args, **kwargs):
        start = time.perf_counter()
        f(*args, **kwargs)
        return time.perf_counter() - start
    return inner

@function_timer
def test_online_load():
    df = pd.read_pickle("https://squeemos.pythonanywhere.com/static/local_storage.xz")

@function_timer
def test_online_db():
    db = tinydb.TinyDB("https://squeemos.pythonanywhere.com/static/youtube.json", storage = OnlineBetterJSONStorage)
    table = db.table("TRENDING")
    df = pd.DataFrame(table)

def main():
    num_iters = 1
    online_db = [test_online_db() for _ in tqdm(range(num_iters))]
    online_df = [test_online_load() for _ in tqdm(range(num_iters))]

    print(f"Average time for online DB: {np.mean(online_db):.3f}")
    print(f"Average time for online DF: {np.mean(online_df):.3f}")

    if True:
        db = tinydb.TinyDB("https://squeemos.pythonanywhere.com/static/youtube.json", storage = OnlineBetterJSONStorage)
        table = db.table("TRENDING")
        pd.to_pickle(pd.DataFrame(table),
            "./local_storage.xz",
            compression = {"method" : "xz"},
            protocol = -1)

if __name__ == '__main__':
    main()
