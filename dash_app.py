# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# Dash things
from dash import Dash, html, dcc, Input, Output, State

# Everything else
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

import tinydb
from ytdb.storage import OnlineBetterJSONStorage

app = Dash()

app.layout = html.Div(children=[
    html.H1(children = "YouTube API Dashboard"),

    html.Div(children = "A simple dashboard for ineracting with and exploring YouTube API data"),

    html.Div([
        dcc.Dropdown(id = "data-set", multi = False, value = "TRENDING",
            options = [{"label" : "TRENDING" , "value" : "TRENDING"}]
        )
    ]),

    dcc.Slider(1, 20, 1,
               value = 5,
               id = "view_slider"
    ),

    dcc.Store(id = "dataframe", storage_type = "memory", data = []),
    dcc.Graph(id = "views_based_on_slider")
])

@app.callback(
    Output("dataframe", "data"),
    Input("data-set", "value")
)
def generate_dataframe(value):
    data_base = tinydb.TinyDB("https://squeemos.pythonanywhere.com/static/youtube.json", storage = OnlineBetterJSONStorage)
    df = pd.DataFrame(data_base.table(value))
    return df.to_dict()
    #df = pd.read_pickle("https://squeemos.pythonanywhere.com/static/local_storage.xz")
    #return df.to_dict(), {}

@app.callback(
    Output("views_based_on_slider", "figure"),
    [Input("view_slider", "value"),
    Input("dataframe", "data")])
def update_view_count_graph(view_slider, data):
    video_views = int(view_slider) * 1_000_000

    df = pd.DataFrame(data)

    ids = df[df["viewCount"] >= video_views]["id"].unique()
    result = df[df["id"].isin(ids)]
    new_fig = px.line(result,
        x = "queryTime",
        y = "viewCount",
        color = "title",
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
