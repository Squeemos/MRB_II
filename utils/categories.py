import json
from urllib.request import urlopen

class YouTubeCategories(object):
    '''
        Container of categories. Contains the key : values which are Category objects
    '''
    class YouTubeCategory(object):
        '''
            Categories object that's basically a key : value pair where the value is a list
        '''
        def __init__(self, key, value):
            self.__key = key
            self.__value = value

        def __eq__(self, other):
            '''
                Because values are keys, a == this is when a is in value
            '''
            return other in self.__value

        def __str__(self) -> str:
            return f"{self.__key} : {self.__value}"

        def __repr__(self) -> str:
            return f"YouTubeCategory: <Key, {self.__key}>, <Value, {self.__value}>"

    def __init__(self, path, local = False):
        '''
            Arguments:
                path  : String path to thing to open
                local : Whether to load using urllib or json load
        '''
        if local:
            with open(path) as link:
                data = json.load(link)
        else:
            with urlopen(path) as link:
                data = json.load(link)

        # Dictionary of id : category
        self.__id_to_title = {int(item["id"]) : item["snippet"]["title"] for item in data["items"]}

        # Dictionary of category : list(ids)
        self.__title_to_id = {}
        for key, value in self.__id_to_title.items():
            if value in self.__title_to_id:
                self.__title_to_id[value].append(key)
            else:
                self.__title_to_id[value] = [key]

    def __getitem__(self, item):
        '''
            Overload of operator[]

            Arguments:
                item : What to get
        '''
        # If it's a single string, get the object there
        if isinstance(item, str):
            return YouTubeCategories.YouTubeCategory(item, self.__title_to_id[item])
        # If it's a list of strings, get all ids as a list
        elif isinstance(item, list):
            cats = []
            for val in item:
                cats.extend(self.__title_to_id[val])
            return cats

    @property
    def titles(self) -> list:
        return list(self.__title_to_id.keys())

    @property
    def title_to_id(self) -> dict:
        return self.__title_to_id

    @property
    def id_to_title(self) -> dict:
        return self.__id_to_title
