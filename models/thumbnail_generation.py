import cv2
from PIL import Image
from requests import get
import pandas as pd
import numpy as np

# Local imports
from yt_utils import YouTubeAccessor
from yt_utils import youtube_image_downloader

def main():
    df = pd.read_feather("https://squeemos.pythonanywhere.com/static/yt_trending.feather")
    keys = ["thumbnails", "high", "url"]
    local_path = "./imgs/"
    what = "categoryId"
    youtube_image_downloader(df, keys, local_path, what)

if __name__ == '__main__':
    main()
