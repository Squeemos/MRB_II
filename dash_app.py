# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# Dash things
from dash import Dash, html, dcc, Input, Output

# Everything else
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

app = Dash()
db = pd.read_pickle("https://squeemos.pythonanywhere.com/static/local_storage.xz")
db["queryTime"] = pd.to_datetime(db["queryTime"])

new_fig = go.Figure()

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Slider(1, 20, 1,
               value = 5,
               id = "view_slider"
    ),

    dcc.Graph(
        id = "views_based_on_slider",
        figure = new_fig
    )
])

@app.callback(
    Output("views_based_on_slider", "figure"),
    Input("view_slider", "value"))
def update_view_count_graph(view_slider):
    video_views = int(view_slider) * 1_000_000
    result = db[db["viewCount"] >= video_views]
    new_fig = px.line(result,
        x = "queryTime",
        y = "viewCount",
        color = "title",
        title = f"Videos with over {video_views:,} views",
        labels = {
            "queryTime" : "Date",
            "viewCount" : "Views in Millions",
            "title" : "Video Title"
            }
        )
    return new_fig

if __name__ == '__main__':
    app.run_server(debug=True)
