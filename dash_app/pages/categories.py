from dash import Dash, html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from flask_caching import Cache

import plotly.express as px
import plotly.figure_factory as ff

from navbar import create_navbar
from app import app, cats, get_dataframe, get_last

def categories_page():
    return html.Div([
        create_navbar(),
        html.H3("Page for interacting with the categories data"),
        html.H4("WARNING: VERY SLOW"),
        html.Div(id = "empty"),
        dcc.Dropdown(
            options = cats.titles,
            id = "trending_category_id",
        ),
        dcc.Graph(id = "category_trending"),
        dcc.Graph(id = "category_taglen"),
    ])


@app.callback(
    Output("category_trending", "figure"),
    [Input("trending_category_id", "value")],
)
def update_category_trending(category_trending):
    if category_trending is not None and category_trending != [None]:
        df = get_dataframe("categories")
        df = df[df.yt["categoryId"] == cats[category_trending]]

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
    Output("category_taglen", "figure"),
    [Input("empty", "value")]
)
def update_category_taglen(value):
    df = get_dataframe("categories")
    df = get_last(df)
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
