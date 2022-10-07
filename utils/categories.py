# Categories
from enum import Enum
import json
from urllib.request import urlopen

class YouTubeCategories(object):
    def __init__(self, path, local = False):
        if local:
            with open(path) as link:
                data = json.load(link)
        else:
            with urlopen(path) as link:
                data = json.load(link)
        self.__dictionary = {item["snippet"]["title"] : int(item["id"]) for item in data["items"]}
        self.__categories = Enum("Categories", self.__dictionary)

    def __getitem__(self, item):
        return self.__categories[item]

    def get_list(self):
        return list(self.__dictionary.keys())

    @property
    def t_to_i(self):
        return self.__dictionary

    @property
    def i_to_t(self):
        return {v:k for k,v in self.__dictionary.items()}
