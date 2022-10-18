import pandas as pd
import numpy as np
import yaml
import os
from PIL import Image
from requests import get
import time
from itertools import repeat

from multiprocessing import Pool
import argparse

from yt_utils import YouTubeAccessor

# Download a video from a url
def download_video(url, what, local_path, key, counter):
    '''
        Arguments:
            url: str url to the image
            what: the thing this specific image belongs to (ex. category)
            local_path: the local path to save the image to (must exist)
            key: used to process the image a specific way
            counter: a counter for a unique number to name the file
    '''
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

    print("Downloading dataframe...")
    if args.url:
        df = pd.read_feather(args.url)
    else:
        raise Exception("Must pass in url")
    print("Dataframe downloaded\nBeginning extraction...")

    # Process the data and set it up to become arguments for the function
    df = df.drop_duplicates(subset = df.yt.get_alias(args.key))
    df = df[df.yt[args.key] != None]
    df = df[[df.yt.get_alias(args.key), df.yt.get_alias(args.what)]]
    range_len = range(len(df))

    print("Extraction complete")

    # Create an iterable with all the function arguments
    arrs = zip(df.yt[args.key].values,
               df.yt[args.what],
               repeat(args.local_path),
               repeat(args.key),
               range(len(df))
           )

    # Create the folders if they don't exist
    if not os.path.exists(args.local_path):
        os.mkdir(args.local_path)

    for val in df.yt[args.what].unique():
        if not os.path.exists(f"{args.local_path}/{val}"):
            os.mkdir(f"{args.local_path}/{val}")

    start_time = time.perf_counter()
    # Create pool
    with Pool(args.num_processes) as p:
        print("Starting pool...")
        # Asynchronous processing
        p.starmap_async(download_video, arrs).get()
        print("Processes completed")
    print(f"Took {time.perf_counter() - start_time:4.4f} seconds")

if __name__ == "__main__":
    main()
