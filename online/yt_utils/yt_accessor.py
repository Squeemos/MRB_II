import pandas as pd
import re

@pd.api.extensions.register_dataframe_accessor("yt")
class YouTubeAccessor(object):

    aliases = {
        # Statistics
        "likeCount" : "statistics.likeCount",
        "viewCount" : "statistics.viewCount",
        "favoriteCount" : "statistics.favoriteCount",
        "commentCount" : "statistics.commentCount",

        # Snippet
        "publishedAt": "snippet.publishedAt",
        "channelId": "snippet.channelId",
        "title" : "snippet.title",
        "description": "snippet.description",
        "channelTitle": "snippet.channelTitle",
        "categoryId" : "snippet.categoryId",
        "tags" : "snippet.tags",

        # Content Details
        "duration" : "contentDetails.duration",

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

        # Use tuple to get to single column
        elif isinstance(item, tuple):
            return self.__df[self.__multiple_index_alias(item)]

        # Multiple columns to get
        elif isinstance(item, list):
            new_cols = []
            for val in item:
                # If the value is a tuple, try to convert with multiple alias
                if isinstance(val, tuple):
                    new_cols.append(self.__multiple_index_alias(val))
                # If it's a string, just get the alias
                elif isinstance(val, str):
                    new_cols.append(self.get_alias(val))
                else:
                    raise NotImplementedError(f"Indexing with {type(val)} is not currentl supported")
            return self.__df[new_cols]

        else:
            raise NotImplementedError(f"Indexing with {type(item)} is not currently supported")

    def __multiple_index_alias(self, item):
        # Unpack because the first item is the harder thing to find
        first, *rest = item
        first = self.get_alias(first)
        # String concatenate them all together with periods
        for val in rest:
            first += "." + val

        return first

    def get_alias(self, item):
        # If it's a string, just check the lookup
        if isinstance(item, str):
            return YouTubeAccessor.aliases.get(item, item)

        # If it's a tuple, we need to try to convert from multiple idnex
        elif isinstance(item, tuple):
            return self.__multiple_index_alias(item)

        else:
            raise NotImplementedError(f"Aliases with {type(item)} is not currently supported")

    @staticmethod
    def convert_pt_to_seconds(string):
        times = re.findall(r"\d+", string)
        match len(times):
            # Seconds
            case 1:
                return int(times[0])
            # Minutes, seconds
            case 2:
                minutes, seconds = times
                return int(minutes) * 60 + int(seconds)
            # Hours, minutes, seconds
            case 3:
                hours, minutes, seconds = times
                return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
            # Days, hours, minutes, seconds
            case 4:
                days, hours, minutes, seconds = times
                return int(days) * 86400 + int(hours) * 3600 + int(minutes) * 60 + int(seconds)
            # Something unexpected
            case _:
                raise Exception(f"More than 4 things parts to the time. {string} {times}")
