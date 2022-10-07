# Categories
from enum import Enum
import json
from urllib.request import urlopen

class YouTubeCategories(object):
    # Maybe there's a good way to load the categories with this but I'm not sure
    categories_url = "https://squeemos.pythonanywhere.com/static/video_categories.json"
    categories_path = "./database/video_categories.json"

    def __init__(self, local = False):
        if local:
            raise NotImplementedError
        else:
            with urlopen(YouTubeCategories.categories_url) as link:
                data = json.load(link)
                self.__dictionary = {item["snippet"]["title"] : int(item["id"]) for item in data["items"]}
                self.__categories = Enum("Categories", self.__dictionary)

    def __getitem__(self, item):
        return self.__categories[item]

    def get_list(self):
        return list(self.__dictionary.keys())
