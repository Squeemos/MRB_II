"""For tag visualizations."""

from collections import Counter

import pandas as pd
import nltk

from etl import misc

nltk.download('stopwords')
STOPWORDS = nltk.corpus.stopwords.words("english")


def cat_tags(df, categories):
    ts = misc.start_timer("category ETL")

    # Remove features containing the following strings
    drops = (
        "localizations", "liveStreamingDetails", "recordingDetails",
        "regionRestriction", "ytRating", "thumbnails", "defaultLanguage",
    )
    tag_df = df.loc[:, [col for col in df.columns if not any(d in col for d in drops)]]

    # Get only last month of data with tokenized/lowered/stopword-free tags
    tag_df = misc.last_month(tag_df)
    tag_df = tag_df.dropna(subset="snippet.tags")
    tag_df["tags"] = tag_df["snippet.tags"].apply(__tokenize_tags)

    # CREATE DFS --------------------------------------------------------------

    # Save df for tag count histogram
    _tag_hist(tag_df, categories)

    misc.end_timer("category ETL", ts)


# Histogram

def _tag_hist(tag_df, categories):
    # Get only latest videos
    cat_tags = tag_df.drop_duplicates(subset="id", keep="last", ignore_index=True)

    # Get tags for each category
    cat_tags = cat_tags.groupby("snippet.categoryId")["tags"].sum()

    # Create column for category id and category name
    cat_tags = pd.DataFrame(cat_tags).reset_index()
    cat_tags["category"] = cat_tags["snippet.categoryId"].apply(lambda x: categories.id_to_title[x])

    # Count tags and get top 10
    cat_tags["tags"] = cat_tags["tags"].apply(Counter)
    cat_tags["tags"] = cat_tags["tags"].apply(lambda x: dict(x.most_common(10)))

    cat_tags["counts"] = cat_tags["tags"].apply(lambda x: list(x.values()))
    cat_tags["tags"] = cat_tags["tags"].apply(lambda x: list(x.keys()))

    # Save result
    misc.save_df(cat_tags, "cat_tags_hist")


# Helpers

def __tokenize_tags(tags):
    out = " ".join(tags).lower().split()
    out = [w for w in out if w not in STOPWORDS]
    return out
