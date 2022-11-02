from dash import Dash, html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from flask_caching import Cache

# Local imports
from yt_utils import YouTubeAccessor
from yt_utils import YouTubeCategories

import pandas as pd
import yaml
import numpy as np

with open("../config.yaml") as stream:
    total_config = yaml.safe_load(stream)

cats = YouTubeCategories(total_config["PATHS"]["CATEGORY_IDS"], local = total_config["LOCAL"])

app = Dash(**total_config["APP_CONFIG"], external_stylesheets = [dbc.themes.MINTY])
# Global cache?
cache = Cache()
cache.init_app(app.server, config = total_config["CACHE_CONFIG"])

@cache.memoize(timeout = 3000)
def get_dataframe(what):
    return pd.read_feather(total_config["PATHS"][what.upper()])

@cache.memoize(timeout = 300)
def get_dataframe_last(what):
    df = get_dataframe(what)
    return df.drop_duplicates(subset = df.yt.get_alias("id"), keep = "last", ignore_index = True).copy()

@cache.memoize(timeout = 3000)
def get_dataframe_last_log_duration_catname(what):
    df = get_dataframe_last(what)
    df[df.yt.get_alias("duration")] = df.yt["duration"].apply(df.yt.convert_pt_to_seconds)
    df["log_duration"] = df.yt["duration"].apply(np.log)
    df["categoryName"] = df.yt["categoryId"].map(cats.id_to_title)
    return df
