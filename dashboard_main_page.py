import streamlit as st
import os
import json
from urllib.request import urlopen
import tinydb
from ytdb.storage import OnlineBetterJSONStorage

@st.experimental_singleton
def get_database(url):
    '''
        Download (and cache) a TinyDB database from a url

        args:
            url : String to url ending with ".json"
    '''
    return tinydb.TinyDB(url, storage = OnlineStorage)

@st.cache(suppress_st_warning=True)
def get_table(database, table_name):
    '''
        Get (and cache) a specific table from a TinyDB database

        args:
            database   : TinyDB databse
            table_name : Name of the table to get
    '''
    return database.table(table_name)

def main():
    page = st.sidebar.selectbox("Pages", ("Opening Page", ))

    db = get_database("https://squeemos.pythonanywhere.com/static/youtube.json")

    if page == "Opening Page":
        trending = get_table(db, "TRENDING")

        sample_query = tinydb.Query()
        result = trending.search(sample_query.viewCount > 10_000_000)

        index = st.slider("Which video with over 10 million views would you like to display?",
            min_value = min(len(result), 0),
            max_value = len(result) - 1,
            step = 1)

        st.image(result[index]["thumbnails"]["high"]["url"])

if __name__ == '__main__':
    main()
