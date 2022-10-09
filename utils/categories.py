import json
from urllib.request import urlopen

class YouTubeCategories(object):
    class YouTubeCategory(object):
        def __init__(self, key, value):
            self.__key = key
            self.__value = value

        def __eq__(self, other):
            return other in self.__value

        def __str__(self):
            return f"{self.__key} : {self.__value}"

        def __repr__(self):
            return f"YouTubeCategory: <Key, {self.__key}>, <Value, {self.__value}>"

    def __init__(self, path, local = False):
        if local:
            with open(path) as link:
                data = json.load(link)
        else:
            with urlopen(path) as link:
                data = json.load(link)

        self.__id_to_title = {int(item["id"]) : item["snippet"]["title"] for item in data["items"]}

        self.__title_to_id = {}
        for key, value in self.__id_to_title.items():
            if value in self.__title_to_id:
                self.__title_to_id[value].append(key)
            else:
                self.__title_to_id[value] = [key]

    def __getitem__(self, item):
        return YouTubeCategories.YouTubeCategory(item, self.__title_to_id[item])

    @property
    def titles(self) -> list:
        return list(self.__title_to_id.keys())

    @property
    def title_to_id(self) -> dict:
        return self.__title_to_id

    @property
    def id_to_title(self) -> dict:
        return self.__title_to_id
