"""For tag visualizations."""

import pandas as pd

from etl import misc


def cat_tags(df, categories):
    # Get only last month of data
    #df = misc.last_month(df)
    df = pd.DataFrame()

    misc.save_df(df, "test")

    pass


def _example(df):
    pass
