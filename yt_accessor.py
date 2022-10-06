import pandas as pd

@pd.api.extensions.register_dataframe_accessor("yt")
class YTAccessor(object):

    aliases = {
        "likeCount" : "statistics.likeCount"
    }

    def __init__(self, df):
        self.__df = df

    def get(self, item):
        key = YTAccessor.aliases.get(item, item)
        return self.__df[key]

    def __getitem__(self, item):
        return self.get(item)
