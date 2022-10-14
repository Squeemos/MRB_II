import pandas as pd

@pd.api.extensions.register_dataframe_accessor("yt")
class YouTubeAccessor(object):

    aliases = {
        # Single strings to get
        "likeCount" : "statistics.likeCount",
        "viewCount" : "statistics.viewCount",
        "title" : "snippet.title",
        "categoryId" : "snippet.categoryId",

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
            first, *rest = item
            # First item can be aliased
            first = self.get_alias(first)
            for item in rest:
                first += "." + item

            return self.__df[first]

        else:
            raise NotImplementedError(f"Indeixing with {type(item)} is not currently supported")

    def get_alias(self, item):
        return YouTubeAccessor.aliases.get(item, item)
