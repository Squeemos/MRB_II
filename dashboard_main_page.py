import streamlit as st
import tinydb
import datetime
from matplotlib import pyplot as plt
import pandas as pd

from ytdb.storage import OnlineJSONStorage

@st.experimental_singleton
def get_database(url):
    '''
        Download (and cache) a TinyDB database from a url

        args:
            url : String to url ending with ".json"
    '''
    return tinydb.TinyDB(url, storage = OnlineJSONStorage)

@st.experimental_singleton
def get_table(_database, table_name):
    '''
        Get (and cache) a specific table from a TinyDB database

        args:
            database   : TinyDB databse
            table_name : Name of the table to get
    '''
    return _database.table(table_name)

def main():
    st.set_page_config(layout = "wide")
    page = st.sidebar.selectbox("Pages",
        ("Opening Page",
        "Playground", )
    )

    db = get_database("https://squeemos.pythonanywhere.com/static/youtube.json")
    trending = get_table(db, "TRENDING")

    if page == "Opening Page":
        sample_query = tinydb.Query()
        result = trending.search(sample_query.viewCount > 5_000_000)

        index = st.slider("Which video with over 10 million views would you like to display?",
            min_value = min(len(result), 0),
            max_value = len(result) - 1,
            step = 1)

        st.image(result[index]["thumbnails"]["high"]["url"])
        st.write(result[index])

    elif page == "Playground":
        view_count_min = st.sidebar.slider("How many views should the video have?",
            min_value = 1,
            max_value = 20,
            value = 5,
            step = 1)
        log_scale = st.sidebar.checkbox("Toggle y-axis log scale")

        sample_query = tinydb.Query()
        result = trending.search(sample_query.viewCount >  (view_count_min * 1_000_000))
        ids = set(video["id"] for video in result)

        df = pd.DataFrame(result)
        df["queryTime"] = pd.to_datetime(df["queryTime"])

        fig = plt.figure(figsize = (20, 10))
        plt.title(f"Views for Trending Videos With Over {view_count_min} million views")
        plt.xlabel("Date")
        plt.ylabel("View Count")
        plt.xticks(rotation = 90)
        if log_scale:
            plt.yscale("log")

        for id in ids:
            title_query = tinydb.Query()
            vids_with_specific_id = trending.search(title_query.id == id)
            title = vids_with_specific_id[0]["title"]
            sub_df = df[df["id"] == id]
            plt.plot(sub_df["queryTime"], sub_df["viewCount"], label = title)

        plt.legend()
        st.pyplot(fig)

if __name__ == '__main__':
    main()
