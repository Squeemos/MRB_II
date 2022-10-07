import pandas as pd

@pd.api.extensions.register_dataframe_accessor("yt")
class YouTubeAccessor(object):

    aliases = {
        "likeCount" : "statistics.likeCount",
        "viewCount" : "statistics.viewCount",
        "title" : "snippet.title",
        "categoryId" : "snippet.categoryId"
    }

    # df is the dataframe to access
    def __init__(self, df):
        self.__df = df

    def get(self, item):
        return self.__df[self.get_alias(item)]

    def __getitem__(self, item):
        return self.get(item)

    def get_alias(self, item):
        return YouTubeAccessor.aliases.get(item, item)
