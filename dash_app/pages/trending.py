from dash import Dash, html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.figure_factory as ff

import numpy as np

from navbar import create_navbar
from app import app, total_config, cats, get_dataframe, process_duration_category

def trending_page():
    return html.Div([
        create_navbar(),
        html.H3("Page for interacting with the trending tab"),
        html.Div(id = "empty"),
        # Dropdown to select video category
        dcc.Dropdown(
            options = cats.titles,
            multi = True,
            id = "category_id",
        ),
        # Simple slider to select values
        # To get the value from the slider, look at "id" and load "value"
        dcc.Slider(0, 20, 1,
                   value = 5,
                   id = "view_slider",
        ),
        dcc.Graph(id = "views_based_on_slider"),
        dcc.Graph(id = "bar_chart_categories"),
        dcc.Graph(id = "trending_box_chart"),
        dcc.Graph(id = "log_duration_hist"),
    ])

@app.callback(
    Output("views_based_on_slider", "figure"),
    [Input("view_slider", "value"),
    Input("category_id", "value")],
)
def update_view_count_graph(view_slider, category_id):
    # Convert to int and the dataframe
    video_views = int(view_slider) * 1_000_000

    df = get_dataframe("trending")

    # Perform the query
    ids = df[df.yt["viewCount"] >= video_views]["id"].unique()
    df = df[df.yt["id"].isin(ids)]
    # Only look at a certain category
    if category_id is not None and len(category_id) != 0:
        category_ids = cats[category_id]
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
    df = get_dataframe("trending")
    df = df.drop_duplicates(df.yt.get_alias("id"))
    grouped = df.groupby(df.yt.get_alias("categoryId")).size().reset_index().copy()
    grouped.columns = [grouped.yt.get_alias("categoryId"), "count"]
    if category_id is not None and len(category_id) != 0:
        category_ids = cats[category_id]

        # Prevent copy problem
        grouped = grouped[grouped.yt["categoryId"].isin(category_ids)].copy()

    grouped[grouped.yt.get_alias("categoryId")] = grouped[grouped.yt.get_alias("categoryId")].map(cats.id_to_title)

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
    Output("trending_box_chart", "figure"),
    [Input("empty", "value")],
)
def update_trending_box_chart(value):
    df = get_dataframe("trending")
    df = process_duration_category(df)
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
    df = get_dataframe("trending")
    df = process_duration_category(df)
    unique_cats = df.yt["categoryName"].unique()
    all_values = [df[df.yt["categoryName"] == cat]["log_duration"] for cat in unique_cats]

    new_fig = ff.create_distplot(
        all_values,
        unique_cats,
        curve_type = "kde",
    )
    return new_fig
