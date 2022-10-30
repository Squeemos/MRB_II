"""Entry point for backend data ETL."""

import yaml
import time

import pandas as pd

from yt_utils import YouTubeCategories

import misc

# ETL function imports
from _cat.tags import cat_tags


# Load config with data paths and indication if local or online
with open("../config.yaml") as stream:
    total_config = yaml.safe_load(stream)


def main():
    ts = misc.start_timer("load")

    # Load trending data
    df_trend = pd.read_feather(total_config["PATHS"]["TRENDING"])

    # Load categories data
    df_cat = pd.read_feather(total_config["PATHS"]["CATEGORIES"])

    # Load categories
    categories = YouTubeCategories(total_config["PATHS"]["CATEGORY_IDS"],
                                   local=total_config["LOCAL"])

    misc.end_timer("load", ts)

    # Perform ETL and save output in data folder
    call_trending_etl(df_trend, categories)
    call_category_etl(df_cat, categories)


def call_trending_etl(df_trend, categories):
    # ADD/REMOVE TRENDING ETL FUNCTIONS
    trend_fns = [


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


if __name__ == "__main__":
    main()
