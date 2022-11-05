from dash import Dash, html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from flask_caching import Cache

# Local imports
from yt_utils import YouTubeAccessor
from yt_utils import YouTubeCategories

import pandas as pd
import yaml
import numpy as np
from datetime import date, datetime, time, timedelta
import warnings


with open("../config.yaml") as stream:
    total_config = yaml.safe_load(stream)

cats = YouTubeCategories(total_config["PATHS"]["CATEGORY_IDS"], local = total_config["LOCAL"])

app = Dash(__name__, **total_config["APP_CONFIG"], external_stylesheets = [dbc.themes.MINTY])
# Global cache?
# cache = Cache()
# cache.init_app(app.server, config = total_config["CACHE_CONFIG"])

# Globals
trending_df = None
categories_df = None

last_load_trending = None
last_load_categories = None

def get_dataframe(what):
    global trending_df
    global categories_df
    global last_load_trending
    global last_load_categories

    dataframe = None
    if what == "trending":
        if trending_df is None or last_load_trending <= datetime.now() - timedelta(hours = 1):
            print("Loading trending...")
            trending_df = pd.read_feather(total_config["PATHS"]["TRENDING"])
            last_load_trending = datetime.now()
        dataframe = trending_df
    elif what == "categories":
        if categories_df is None or last_load_categories <= datetime.now() - timedelta(hours = 1):
            print("Loading categories...")
            categories_df = pd.read_feather(total_config["PATHS"]["CATEGORIES"])
            last_load_categories = datetime.now()
        dataframe = categories_df
    else:
        warnings.warn("Requesting a dataframe that does not exist")
    return dataframe


def get_last(df):
    return df.drop_duplicates(subset = df.yt.get_alias("id"), keep = "last", ignore_index = True).copy()

def process_duration_category(df):
    df = get_last(df)
    df[df.yt.get_alias("duration")] = df.yt["duration"].apply(df.yt.convert_pt_to_seconds)
    df["log_duration"] = df.yt["duration"].apply(np.log)
    df["categoryName"] = df.yt["categoryId"].map(cats.id_to_title)
    return df
