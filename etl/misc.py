"""Misc. ETL utility fns."""

import time
import pandas as pd


def last_month(df: pd.DataFrame, time_feature_name: str = "queryTime"):
    """Returns only last month of given data based on the given feature.

    Parameters
        df: DataFrame to reduce to only last month's data
        time_feature_name: Name of time feature to use to
    """
    return df.set_index(time_feature_name).last("30D").reset_index()


def save_df(df: pd.DataFrame, name: str):
    """Saves given dataframe in etl/data with given name (NOT filename).

    Parameters:
        df: DataFrame to be saved
        name: Name (NOT filename) if dataframe to save

    Example:
        save_df(df, 'tag_hist') --> etl/data/tag_hist.xz
    """
    df.to_feather(f"data/{name}.feather", compression="zstd")


def start_timer(task_name: str):
    print(f"Starting {task_name}...")
    return time.perf_counter()


def end_timer(task_name: str, ts: float):
    print(f"Finished {task_name} in {time.perf_counter() - ts} sec.")
