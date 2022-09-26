import streamlit as st

import tinydb
import datetime
from matplotlib import pyplot as plt
import pandas as pd
from PIL import Image
import requests
from io import BytesIO

# Local imports
from ytdb.storage import OnlineBetterJSONStorage

@st.experimental_singleton
def get_database(url):
    '''
        Download (and cache) a TinyDB database from a url

        args:
            url : String to url ending with ".json"
    '''
    return tinydb.TinyDB(url, storage = OnlineBetterJSONStorage)

@st.experimental_singleton
def get_table(_database, table_name):
    '''
        Get (and cache) a specific table from a TinyDB database

        args:
            database   : TinyDB databse
            table_name : Name of the table to get
    '''
    return _database.table(table_name)

@st.experimental_singleton
def sidebar_buttons_overtime(id):
    return []

@st.experimental_memo
def get_all_ids(_table):
    all_ids = set()
    for entry in _table:
        if isinstance(entry["id"], str):
            all_ids.add(entry["id"])
    return list(all_ids)

def main():
    # Config
    st.set_page_config(layout = "wide")

    page = st.sidebar.selectbox("Pages",
        ("Opening Page",
        "Read Data",
        "Query Maker",
        "Playground", )
    )

    db = get_database("https://squeemos.pythonanywhere.com/static/youtube.json")
    trending = get_table(db, "TRENDING")

    if page == "Opening Page":
        sample_query = tinydb.Query()
        result = trending.search(sample_query.viewCount > 5_000_000)

        index = st.slider("Which video with over 10 million views would you like to display?",
            min_value = min(len(result), 0),
            max_value = max(len(result) - 1, 0),
            step = 1)

        st.image(result[index]["thumbnails"]["high"]["url"])
        st.write(result[index])

    elif page == "Read Data":
        index = st.slider("Look over specific video data",
            min_value = min(len(trending), 0),
            max_value = max(len(trending) - 1, 0),
            step = 1
        )
        sorted_table = sorted(trending.all(), key = lambda k:k.doc_id)
        st.write(sorted_table[index])

    elif page == "Query Maker":
        sidebar_buttons = sidebar_buttons_overtime(0)
        button_add = st.sidebar.button("Add a query")
        button_pop = st.sidebar.button("Remove last query")

        if button_add:
            sidebar_buttons.append(f"Q{len(sidebar_buttons)}")
        if button_pop and len(sidebar_buttons):
            sidebar_buttons.pop()


        st.write(sidebar_buttons)

    elif page == "Playground":
        if st.sidebar.checkbox("Display graphs for trending videos"):
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

            for id_val in ids:
                title_query = tinydb.Query()
                vids_with_specific_id = trending.search(title_query.id == id_val)
                title = vids_with_specific_id[0]["title"]
                sub_df = df[df["id"] == id_val]
                plt.plot(sub_df["queryTime"], sub_df["viewCount"], label = title)

            plt.legend()
            st.pyplot(fig)

        if st.sidebar.checkbox("Look through video thumbnails"):
            all_ids = get_all_ids(trending)
            title_query = tinydb.Query()
            all_titles = {trending.search(title_query.id == id_val)[0]["title"]:id_val for id_val in all_ids}
            title = st.selectbox("Which video thumbnail would you like to see?", all_titles)
            specific_id = all_titles[title]

            thumbnail = trending.search(title_query.id == specific_id)[0]["thumbnails"]
            if (tnail := thumbnail.get("maxres")) is not None:
                url = tnail["url"]
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))
                st.image(img)
            elif (tnail := thumbnail.get("high")) is not None:
                st.image(tnail["url"])
            else:
                st.write("This image doesn't have a thumbnail?")

if __name__ == '__main__':
    main()
