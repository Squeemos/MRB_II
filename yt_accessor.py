import pandas as pd

# Categories
from enum import Enum
import json
from urllib.request import urlopen

@pd.api.extensions.register_dataframe_accessor("yt")
class YTAccessor(object):

    aliases = {
        "likeCount" : "statistics.likeCount"
    }

    # Maybe there's a good way to load the categories with this but I'm not sure
    categories_url = "https://squeemos.pythonanywhere.com/static/video_categories.json"
    categories_path = "./database/video_categories.json"

    # df is the dataframe to access
    def __init__(self, df):
        self.__df = df

    def get(self, item):
        key = YTAccessor.aliases.get(item, item)
        return self.__df[key]

    def __getitem__(self, item):
        return self.get(item)

    def get_alias(self, item):
        return YTAccessor.aliases.get(item, item)

# Right now, loading the categories is a function
def get_categories(local = False):
    categories_url = "https://squeemos.pythonanywhere.com/static/video_categories.json"
    categories_path = "./database/video_categories.json"

    if local:
        return None
    else:
        with urlopen(categories_url) as link:
            data = json.load(link)
            return Enum("Categories", {item["snippet"]["title"] : int(item["id"]) for item in data["items"]})
