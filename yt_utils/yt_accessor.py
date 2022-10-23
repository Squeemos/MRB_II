import pandas as pd

@pd.api.extensions.register_dataframe_accessor("yt")
class YouTubeAccessor(object):

    aliases = {
        # Statistics
        "likeCount" : "statistics.likeCount",
        "viewCount" : "statistics.viewCount",

        # Snippet
        "publishedAt": "snippet.publishedAt",
        "channelId": "snippet.channelId",
        "title" : "snippet.title",
        "description": "snippet.description",
        "channelTitle": "snippet.channelTitle",
        "categoryId" : "snippet.categoryId",
        "tags" : "snippet.tags",

        # These must be used with df.yt[one, two, three, ...]
        "thumbnails" : "snippet.thumbnails",
    }

    # df is the dataframe to access
    def __init__(self, df):
        self.__df = df

    def get(self, item):
        return self.__df[self.get_alias(item)]

    def __getitem__(self, item):
        # Single string
        if isinstance(item, str):
            return self.get(item)

        # Multiple indexing
        elif isinstance(item, (list, tuple)):
            return self.__df[self.__multiple_index_alias(item)]

        else:
            raise NotImplementedError(f"Indeixing with {type(item)} is not currently supported")

    def __multiple_index_alias(self, item):
        first, *rest = item
        first = self.get_alias(first)
        for val in rest:
            first += "." + val

        return first

    def get_alias(self, item):
        if isinstance(item, str):
            return YouTubeAccessor.aliases.get(item, item)

        elif isinstance(item, (list, tuple)):
            return self.__multiple_index_alias(item)

        else:
            raise NotImplementedError(f"Aliases with {type(item)} is not currently supported")
