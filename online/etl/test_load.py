"""For checking dataframes in etl/data."""

import pandas as pd


def main():
    fname = "cat_tags_hist"

    df = pd.read_feather(f"data/{fname}.feather")

    print(df.to_string())


if __name__ == "__main__":
    main()
