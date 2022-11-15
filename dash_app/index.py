from dash import Dash, html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc

from app import app
from pages import home, trending, categories, tags

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
        return categories.categories_page()
    elif pathname == "/trending":
        return trending.trending_page()
    elif pathname == "/tags":
        return tags.tags_page()
    else:
        return home.home_page()
