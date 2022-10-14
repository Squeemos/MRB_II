import cv2
from PIL import Image
from requests import get
import pandas as pd
import numpy as np

# Local imports
from utils import YouTubeAccessor

def main():
    df = pd.read_feather("https://squeemos.pythonanywhere.com/static/yt_trending.feather")

    for url in df.yt["thumbnails", "maxres", "url"].values:
        # Some videos don't have maxres thumbnails
        if url is None:
            continue

        # Read image in with pillow and get
        image = Image.open(get(url, stream = True).raw)
        arr = np.array(image)

        # Convert the image to bgr for opencv to display
        bgr_arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

        # The window that shows what we're looking at
        cv2.imshow("View", bgr_arr)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

if __name__ == '__main__':
    main()
