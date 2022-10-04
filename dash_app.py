# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# Dash things
from dash import Dash, html, dcc, Input, Output, State

# Everything else
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

app = Dash()

app.layout = html.Div(children = [
    html.H1(children = "YouTube API Dashboard"),
    html.Div(children = "A simple dashboard for ineracting with and exploring YouTube API data"),

    # Simple slider to select values
    # To get the value from the slider, look at "id" and read "value"
    dcc.Slider(1, 20, 1,
               value = 5,
               id = "view_slider"
    ),

    # Storage of the dataframe in memory, valid until refreshed or closed
    dcc.Store(id = "dataframe", storage_type = "memory", data = []),
    # The graph, to display the graph here, output "figure" to "id"
    dcc.Graph(id = "views_based_on_slider")
])

# Simple callback that stores the dataframe
@app.callback(
    Output("dataframe", "data"),
    Input("dataframe", "data")
)
def generate_dataframe(value):
    return pd.read_pickle("https://squeemos.pythonanywhere.com/static/yt_trending.xz").to_dict()

# Better callback to dispolay some things
# Output is a figure to the dcc.Graph
# Input is the slider and the dataframe
@app.callback(
    Output("views_based_on_slider", "figure"),
    [Input("view_slider", "value"),
    Input("dataframe", "data")])
def update_view_count_graph(view_slider, data):
    # Convert to int and the dataframe
    video_views = int(view_slider) * 1_000_000
    df = pd.DataFrame(data)

    # Perform the query
    ids = df[df["viewCount"] >= video_views]["id"].unique()
    result = df[df["id"].isin(ids)]

    # Create a figure with plotly express
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
