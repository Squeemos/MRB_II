# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# Dash things
from dash import Dash, html, dcc, Input, Output, State
from flask_caching import Cache

# Everything else
import plotly.express as px
import pandas as pd

# Local imports
from yt_accessor import YTAccessor

app = Dash()

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 600
}
cache = Cache()
cache.init_app(app.server, config=config)

app.layout = html.Div(children = [
    html.H1(children = "YouTube API Dashboard"),
    html.Div(children = "A simple dashboard for ineracting with and exploring YouTube API data"),

    # Simple slider to select values
    # To get the value from the slider, look at "id" and read "value"
    dcc.Slider(1, 20, 1,
               value = 5,
               id = "view_slider"
    ),

    # The graph, to display the graph here, output "figure" to "id"
    dcc.Graph(id = "views_based_on_slider")
])

# Simple callback that stores the dataframe
# @app.callback(
#     Output("dataframe", "data"),
#     Input("dataframe", "data")
# )
# def generate_dataframe(value):
#     return pd.read_pickle("https://squeemos.pythonanywhere.com/static/yt_trending.xz").to_dict()

# Get and memoize the dataframe
@cache.memoize(timeout = 600)
def generate_dataframe(url):
    return pd.read_pickle(url)

# Better callback to dispolay some things
# Output is a figure to the dcc.Graph
# Input is the slider
@app.callback(
    Output("views_based_on_slider", "figure"),
    [Input("view_slider", "value")])
def update_view_count_graph(view_slider):
    # Convert to int and the dataframe
    video_views = int(view_slider) * 1_000_000
    df = generate_dataframe("https://squeemos.pythonanywhere.com/static/archive.xz") # Change to updated one later

    # Perform the query
    ids = df[df["viewCount"] >= video_views]["id"].unique()
    df = df[df["id"].isin(ids)]

    # Create a figure with plotly express
    new_fig = px.line(df,
        x = df.yt["queryTime"],
        y = df.yt["viewCount"],
        color = df.yt["title"],
        title = f"Trending lifetime of videos that gained over {video_views:,} views",
        labels = {
            "queryTime" : "Date",
            "viewCount" : "Views in Millions",
            "title" : "Video Title"
            }
        )
    return new_fig

if __name__ == '__main__':
    app.run_server(debug=True)
