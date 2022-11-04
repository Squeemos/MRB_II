from dash import Dash, html, dcc, Input, Output, State, dash_table, register_page
import dash_bootstrap_components as dbc
### Import Dash Instance ###

from navbar import create_navbar
from app import app, get_dataframe

def home_page():
    return html.Div([
        create_navbar(),
        html.H3("Welcome to the home page!"),
        dcc.Markdown(
            """
                ### YouTube API Notice
                By using this dashboard, you agree to comply with [YouTube's Terms of Service](https://www.youtube.com/t/terms)


                This client uses the YouTube API Services and complies with the [Google Privacy Policy.](http://www.google.com/policies/privacy)\n
                This client does not track user data, any data that is cached is strictly for the use of the dashboard and is user independent.\n
                Meaning two independent users could access the dashboard at the same time and view the same data, but the dashboard does not see them as independent users, but just as ambiguous users.

                What this API client does:
                - Display YouTube API data
                - Use YouTube API data to create models such as regression, classification, and others

                What this API client does not do:
                - Access Authorized Data
                - Store Authorized Data
                - Contact third party services to share user data or Authorized data
                - Upload user or Authorized Data to YouTube via this API client
                - Modify or replace any aspect of the data returned to the API client via the YouTube API
            """
        ),
        html.Button('Preload all Data', id = 'button', n_clicks = 0),
        dcc.Loading(
            id = "loading-input-1",
            children = html.Div(id = "loading-output-1"),
            type = "graph",
        ),
    ])

@app.callback(
    Output("loading-output-1", "children"),
    [Input("button", "n_clicks")],
)
def preload_all_data(value):
    if value > 0:
        get_dataframe("trending")
        get_dataframe("categories")
