"""Entry point for backend data ETL."""

import yaml
import os

import pandas as pd

from yt_utils import YouTubeCategories

import misc

# ETL function imports
from _cat.tags import cat_tags

from _trend.views import trend_views


# Load config with data paths and indication if local or online
with open("../config.yaml") as stream:
    total_config = yaml.safe_load(stream)


def main():
    ts = misc.start_timer("load")

    paths = __get_paths()

    # Load trending data
    df_trend = pd.read_feather(paths["TRENDING"])

    # Load categories data
    df_cat = pd.read_feather(paths["CATEGORIES"])

    # Load categories
    categories = YouTubeCategories(paths["CATEGORY_IDS"],
                                   local=total_config["LOCAL"])

    misc.end_timer("load", ts)

    # Create data directory if it does not exist
    if not os.path.isdir("data"):
        os.makedirs("data")

    # Perform ETL and save output in data folder
    call_trending_etl(df_trend, categories)
    call_category_etl(df_cat, categories)


def call_trending_etl(df_trend, categories):
    # ADD/REMOVE TRENDING ETL FUNCTIONS
    trend_fns = [
        trend_views

    ]

    for fn in trend_fns:
        fn(df_trend, categories)


def call_category_etl(df_cat, categories):
    # ADD/REMOVE CATEGORY ETL FUNCTIONS
    cat_fns = [
        cat_tags,

    ]

    for fn in cat_fns:
        fn(df_cat, categories)


def __get_paths():
    paths = {
        "TRENDING": total_config["PATHS"]["TRENDING"],
        "CATEGORIES": total_config["PATHS"]["CATEGORIES"],
        "CATEGORY_IDS": total_config["PATHS"]["CATEGORY_IDS"],
    }

    if total_config["LOCAL"]:
        paths = {k: "." + path for k, path in paths.items()}

    return paths


if __name__ == "__main__":
    main()
