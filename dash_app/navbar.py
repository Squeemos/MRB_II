from dash import Dash, html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
from flask_caching import Cache

def create_navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="Menu",
                children=[
                    dbc.DropdownMenuItem("Home", href = '/'),
                    dbc.DropdownMenuItem(divider = True),
                    dbc.DropdownMenuItem("Trending", href = "/trending"),
                    dbc.DropdownMenuItem("Categories", href = '/categories'),
                    dbc.DropdownMenuItem("Tags", href = '/tags')
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
