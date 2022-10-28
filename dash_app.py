# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# Dash things
from dash import Dash, html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from flask_caching import Cache

# Plotly stuff
import plotly.express as px
import plotly.figure_factory as ff

# Everything else
import pandas as pd
import yaml
import numpy as np
import orjson

# Local imports
from yt_utils import YouTubeAccessor
from yt_utils import YouTubeCategories

with open("./config.yaml") as stream:
    total_config = yaml.safe_load(stream)

app = Dash(**total_config["APP_CONFIG"], external_stylesheets = [dbc.themes.MINTY])
cache = Cache()

cache.init_app(app.server, config = total_config["CACHE_CONFIG"])
categories = YouTubeCategories(total_config["PATHS"]["CATEGORY_IDS"], local = total_config["LOCAL"])

app.layout = html.Div(children = [
    dcc.Location(id = "url", refresh = False),
    html.Div(id = "page-content"),
])

@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def display_page(pathname):
    if pathname == "/categories":
        return categories_page()
    elif pathname == "/trending":
        return trending_page()
    else:
        return page_home()

# Get and memoize the dataframe
@cache.memoize(timeout = 3000)
def get_dataframe(url):
    return pd.read_feather(url)

def create_navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="Menu",
                children=[
                    dbc.DropdownMenuItem("Home", href='/'),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Trending", href = "/trending"),
                    dbc.DropdownMenuItem("Categories", href='/categories'),
                ],
            ),
        ],
        brand="Home",
        brand_href="/",
        sticky="top",
        color="dark",
        dark=True,
    )

    return navbar

def page_home():
    return html.Div([
        create_navbar(),
        html.H3("Welcome to the home page!"),
    ])

def trending_page():
    return html.Div([
        create_navbar(),
        html.H3("Page for interacting with the trending tab"),
        html.Div(id = "empty"),
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
        dcc.Graph(id = "views_based_on_slider"),
        dcc.Graph(id = "bar_chart_categories"),
        dcc.Graph(id = "trending_box_chart"),
        dcc.Graph(id = "log_duration_hist"),
    ])

def categories_page():
    return html.Div([
        create_navbar(),
        html.H3("Page for interacting with the categories data"),
        html.H4("WARNING: VERY SLOW"),
        html.Div(id = "empty"),
        dcc.Dropdown(
            options = categories.titles,
            id = "trending_category_id",
        ),
        dcc.Graph(id = "category_trending"),
        dcc.Graph(id = "category_taglen"),
    ])

@app.callback(
    Output("views_based_on_slider", "figure"),
    [Input("view_slider", "value"),
    Input("category_id", "value")],
)
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
    [Input("category_id", "value")],
    suppress_callback_exceptions = True,
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
    [Input("trending_category_id", "value")],
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


@app.callback(
    Output("trending_box_chart", "figure"),
    [Input("empty", "value")],
)
def update_trending_box_chart(value):
    df = get_dataframe(total_config["PATHS"]["TRENDING"])
    df = df.drop_duplicates(subset = df.yt.get_alias("id"), keep = "last", ignore_index = True).copy()
    df[df.yt.get_alias("duration")] = df.yt["duration"].apply(df.yt.convert_pt_to_seconds)
    df["log_duration"] = df.yt["duration"].apply(np.log)
    df["categoryName"] = df.yt["categoryId"].map(categories.id_to_title)
    new_fig = px.box(
        df,
        x = df.yt.get_alias("categoryName"),
        y = df.yt.get_alias("log_duration"),
        labels = {
            df.yt.get_alias("categoryName") : "Category",
            df.yt.get_alias("log_duration") : "Duration (log scale)",
        }
    )

    return new_fig

@app.callback(
    Output("log_duration_hist", "figure"),
    [Input("empty", "value")],
)
def update_log_duration_hist(value):
    df = get_dataframe(total_config["PATHS"]["TRENDING"])
    df = df.drop_duplicates(subset = df.yt.get_alias("id"), keep = "last", ignore_index = True).copy()
    df[df.yt.get_alias("duration")] = df.yt["duration"].apply(df.yt.convert_pt_to_seconds)
    df["log_duration"] = df.yt["duration"].apply(np.log)
    df["categoryName"] = df.yt["categoryId"].map(categories.id_to_title)

    unique_cats = df.yt["categoryName"].unique()
    all_values = [df[df.yt["categoryName"] == cat]["log_duration"] for cat in unique_cats]

    new_fig = ff.create_distplot(
        all_values,
        unique_cats,
        curve_type = "kde",
    )

    return new_fig

@app.callback(
    Output("category_taglen", "figure"),
    [Input("empty", "value")]
)
def update_category_taglen(value):
    df = get_dataframe(total_config["PATHS"]["CATEGORIES"])
    df = df.drop_duplicates(subset = df.yt.get_alias("id"), keep = "last", ignore_index = True).copy()
    df["tagLen"] = df.yt["tags"].apply(lambda x: len(x) if x is not None else 0)

    new_fig = px.scatter(
        df,
        x = df.yt.get_alias("tagLen"),
        y = df.yt.get_alias("viewCount"),
        color = df.yt.get_alias("title"),
        labels = {
            df.yt.get_alias("tagLen") : "Number of Tags",
            df.yt.get_alias("viewCount") : "Number of Views",
            df.yt.get_alias("title") : "Title",
        },
    )
    return new_fig


if __name__ == '__main__':
    app.run(debug = True)
