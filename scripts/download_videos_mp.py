import pandas as pd
import numpy as np
import yaml
import os
from PIL import Image
from requests import get
import time

from multiprocessing import Pool
import argparse

from yt_utils import YouTubeAccessor

def download_video(url, what, local_path, key, counter):
    img = Image.open(get(url, stream = True).raw)
    arr = np.array(img)
    if "high" in key:
        arr = arr[46:315, :, :]
    img = Image.fromarray(arr)
    img.save(f"{local_path}/{what}/{counter}.png")

def main():
    parser = argparse.ArgumentParser(description = "Download videos using multiprocessing")
    parser.add_argument("--url", "-u", type = str)
    parser.add_argument("--local-path", "-lp", type = str, default = "./imgs/")
    parser.add_argument("--num-processes", "-np", type = int, default = 1)
    parser.add_argument("--key", "-k", type = list, default = ["thumbnails", "high", "url"])
    parser.add_argument("--what", "-w", type = str, default = "categoryId")

    args = parser.parse_args()

    if args.url:
        df = pd.read_feather(args.url)
    else:
        raise Exception("Must pass in url")

    df = df.drop_duplicates(subset = df.yt.get_alias(args.key))
    df = df[[df.yt.get_alias(args.key), df.yt.get_alias(args.what)]]
    range_len = range(len(df))

    arrs = zip(df.yt[args.key].values,
               df.yt[args.what],
               [args.local_path for _ in range_len],
               [args.key for _ in range_len],
               range(len(df))
           )

    if not os.path.exists(args.local_path):
        os.mkdir(args.local_path)

    for val in df.yt[args.what].unique():
        if not os.path.exists(f"{args.local_path}/{val}"):
            os.mkdir(f"{args.local_path}/{val}")

    start_time = time.perf_counter()
    with Pool(args.num_processes) as p:
        print("Starting pool...")
        if "high" in args.key:
            p.starmap(download_video, arrs)
        print("Processes completed")
    print(f"Took {time.perf_counter() - start_time:.4} seconds")

if __name__ == "__main__":
    main()
