from PIL import Image
from requests import get
import numpy as np
import pandas as pd
import os

from .yt_accessor import YouTubeAccessor

from typing import Union

# Groups based on categories
def youtube_image_downloader(df : pd.DataFrame,
                             key : Union[str, list[str], tuple[str]],
                             local_path : str,
                             what : str):
    '''
        Downloads all videos from a dataframe into local folders for loading

        Arguments:
            df:         The DataFrame to get everything from
            key:        The 'key' to get urls from
            local_path: The local path to put files in (does not need to exist)
            what:       The thing to organize images by (does not need to be alias)


        Example:
            youtube_image_downloader(df, ("thumbnails", "high", "url"), "./imgs", "categoryId")
            Example file structure after:
            imgs
            ├── what.0
            │   ├── 0
            │   ├── 5
            │   └── etc
            ├── what.1
            │   ├── 1
            │   ├── 4
            │   ├── 7
            │   ├── 10
            │   ├── 47
            │   └── etc
            └── what.etc
    '''

    # Only get the unique urls to not download duplicates
    new_df = df.drop_duplicates(subset = df.yt.get_alias(key))

    # Trim dataframe to only have key and what
    new_df = new_df[[df.yt.get_alias(key), df.yt.get_alias(what)]]

    # Counter to give each image unique value
    counter = 0

    # If the local path doesn't exist, create it
    if not os.path.exists(local_path):
        os.mkdir(local_path)

    # Create subdirectories if they don't exist
    for val in new_df.yt[what].unique():
        if not os.path.exists(f"{local_path}/{val}"):
            os.mkdir(f"{local_path}/{val}")

    # Currently everything is only tested on "high" quality images
    if "high" in key:
        for url, thing in zip(new_df.yt[key].values, new_df.yt[what]):
            # Create the image from the url
            img = Image.open(get(url, stream = True).raw)
            # Convert to array and remove the black bars
            arr = np.array(img)[46:315, :, :]
            # Convert and save
            img = Image.fromarray(arr)
            img.save(f"{local_path}/{thing}/{counter}.png")
            counter += 1

    else:
        raise NotImplementedError("Currently only supported images are 'high'")
