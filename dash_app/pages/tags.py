from dash import html, dcc, Input, Output

import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from navbar import create_navbar
from app import app, cats, get_dataframe, get_etl, get_last

import pandas as pd

import math

def tags_page():
    return html.Div([
        create_navbar(),
        html.H3("Explore tags"),
        html.Div(id="empty"),
        dcc.Dropdown(
            options=cats.titles,
            id="cat_hist_data",
        ),
        dcc.Graph(id="cat_tags_hist", className="center"),
    ])

@app.callback(
    Output("cat_tags_hist", "figure"),
    [Input("empty", "value")],
)
def tag_hists(value):
    cat_tags = get_etl("cat_tags_hist")

    cat_count = cat_tags.shape[0]
    rows, cols = math.ceil(cat_count / 4), 4

    # Create subplots
    fig = make_subplots(
        rows=rows, cols=cols,
        vertical_spacing=0.06, horizontal_spacing=0.1,
        subplot_titles=cat_tags.category
    )

    # Plot
    cat_idx = 0
    for i in range(rows):
        for j in range(cols):
            data = cat_tags[cat_tags.category == cat_tags.category[cat_idx]]

            fig.append_trace(
                go.Bar(
                    x=list(data["counts"])[0], y=list(data["tags"])[0], orientation="h",
                ),
                row=i + 1, col=j + 1,
            )

            # Quit if all categories done
            cat_idx = cat_idx + 1
            if cat_idx >= cat_count:
                break

    # Layout
    fig.update_layout(
        title_text="YouTube Tag Frequency by Category",
        title_x=0.5,
        showlegend=False,
        autosize=False,
        width=1000,
        height=930,
    )

    return fig

def tag_lines():
    pass
