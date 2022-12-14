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

cat_tags_hist_df = None
cat_tags_hist_load = None

def get_dataframe(what):
    global trending_df
    global categories_df
    global last_load_trending
    global last_load_categories

    dataframe = None
    if what == "trending":
        if _should_reload(trending_df, last_load_trending):
            print("Loading trending...")
            trending_df = pd.read_feather(total_config["PATHS"]["TRENDING"])
            last_load_trending = datetime.now()
        dataframe = trending_df
    elif what == "categories":
        if _should_reload(categories_df, last_load_categories):
            print("Loading categories...")
            categories_df = pd.read_feather(total_config["PATHS"]["CATEGORIES"])
            last_load_categories = datetime.now()
        dataframe = categories_df
    else:
        warnings.warn("Requesting a dataframe that does not exist")
    return dataframe

def get_etl(what):
    global cat_tags_hist_df
    global cat_tags_hist_load

    dataframe = None
    if what == "cat_tags_hist":
        if _should_reload(cat_tags_hist_df, cat_tags_hist_load):
            print("Loading category tags histogram...")
            cat_tags_hist_df = pd.read_feather(total_config["PATHS"]["CAT_TAGS_HIST"])
            cat_tags_hist_load = datetime.now()
        dataframe = cat_tags_hist_df
    else:
        warnings.warn("Requesting a dataframe that does not exist")
    return dataframe

def _should_reload(df, load_time, hours=1):
    return df is None or load_time <= datetime.now() - timedelta(hours=hours)

def get_last(df):
    return df.drop_duplicates(subset = df.yt.get_alias("id"), keep = "last", ignore_index = True).copy()

def process_duration_category(df):
    df = get_last(df)
    df[df.yt.get_alias("duration")] = df.yt["duration"].apply(df.yt.convert_pt_to_seconds)
    df["log_duration"] = df.yt["duration"].apply(np.log)
    df["categoryName"] = df.yt["categoryId"].map(cats.id_to_title)
    return df
