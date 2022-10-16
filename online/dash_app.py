# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# Dash things
from dash import Dash, html, dcc, Input, Output, State, dash_table
from flask_caching import Cache

# Everything else
import plotly.express as px
import pandas as pd
import yaml

# Local imports
from yt_utils import YouTubeAccessor
from yt_utils import YouTubeCategories

with open("./config.yaml") as stream:
    total_config = yaml.safe_load(stream)

app = Dash(**total_config["APP_CONFIG"])
cache = Cache()

cache.init_app(app.server, config = total_config["CACHE_CONFIG"])

categories = YouTubeCategories(total_config["PATHS"]["CATEGORY_IDS"], local = total_config["LOCAL"])

app.layout = html.Div(children = [
    html.H1(children = "YouTube API Dashboard - In Progress"),
    html.Div(children = "A simple dashboard for interacting with and exploring YouTube API data"),

    # Dropdown to select video category
    dcc.Dropdown(
        options = categories.titles,
        multi = True,
        id = "category_id"
    ),

    # Simple slider to select values
    # To get the value from the slider, look at "id" and load "value"
    dcc.Slider(0, 20, 1,
               value = 5,
               id = "view_slider"
    ),

    # The graph, to display the graph here, output "figure" to "id"
    dcc.Graph(id = "views_based_on_slider"),
    dcc.Graph(id = "bar_chart_categories"),

    dcc.Dropdown(
        options = categories.titles,
        id = "trending_category_id",
    ),
    dcc.Graph(id = "category_trending"),
])

# Get and memoize the dataframe
@cache.memoize(timeout = 3000)
def get_dataframe(url):
    return pd.read_feather(url)

# Better callback to display some things
# Output is a figure to the dcc.Graph
# Input is the slider
@app.callback(
    Output("views_based_on_slider", "figure"),
    [Input("view_slider", "value"),
    Input("category_id", "value")])
def update_view_count_graph(view_slider, category_id):
    # Convert to int and the dataframe
    video_views = int(view_slider) * 1_000_000
    df = get_dataframe(total_config["PATHS"]["TRENDING"])

    # Perform the query
    ids = df[df.yt["viewCount"] >= video_views]["id"].unique()
    df = df[df.yt["id"].isin(ids)]
    # Only look at a certain category
    if category_id is not None and len(category_id) != 0:
        category_ids = categories[category_id]
        df = df[df.yt["categoryId"].isin(category_ids)]

    # Create a figure with plotly express
    new_fig = px.line(
        df,
        x = df.yt.get_alias("queryTime"),
        y = df.yt.get_alias("viewCount"),
        color = df.yt.get_alias("title"),
        title = f"Trending lifetime of videos that gained over {video_views:,} views",
        labels = {
            df.yt.get_alias("queryTime") : "Date",
            df.yt.get_alias("viewCount") : "Views in Millions",
            df.yt.get_alias("title") : "Video Title"
        }
    )
    return new_fig

@app.callback(
    Output("bar_chart_categories", "figure"),
    [Input("category_id", "value")]
)
def update_bar_chart_categories(category_id):
    df = get_dataframe(total_config["PATHS"]["TRENDING"])
    df = df.drop_duplicates(df.yt.get_alias("id"))
    grouped = df.groupby(df.yt.get_alias("categoryId")).size().reset_index().copy()
    grouped.columns = [grouped.yt.get_alias("categoryId"), "count"]
    if category_id is not None and len(category_id) != 0:
        category_ids = categories[category_id]

        # Prevent copy problem
        grouped = grouped[grouped.yt["categoryId"].isin(category_ids)].copy()

    grouped[grouped.yt.get_alias("categoryId")] = grouped[grouped.yt.get_alias("categoryId")].map(categories.id_to_title)

    new_fig = px.bar(
        grouped,
        x = grouped.yt.get_alias("categoryId"),
        y = grouped.yt.get_alias("count"),
        color = grouped.yt.get_alias("count"),
        labels = {
            grouped.yt.get_alias("categoryId") : "Category",
            grouped.yt.get_alias("count") : "Number of Videos"
        }
    )

    return new_fig

@app.callback(
    Output("category_trending", "figure"),
    [Input("trending_category_id", "value")]
)
def update_category_trending(category_trending):
    if category_trending is not None and category_trending != [None]:
        df = get_dataframe(total_config["PATHS"]["CATEGORIES"])
        df = df[df.yt["categoryId"] == categories[category_trending]]

        new_fig = px.line(
            df,
            x = df.yt.get_alias("queryTime"),
            y = df.yt.get_alias("viewCount"),
            color = df.yt.get_alias("title"),
            title = f"Videos from {category_trending} trending tab",
            labels = {
                df.yt.get_alias("queryTime") : "Date",
                df.yt.get_alias("viewCount") : "Views",
                df.yt.get_alias("title") : "Title",
            }
        )

        return new_fig
    else:
        return {}



if __name__ == '__main__':
    app.run_server(debug=True)
