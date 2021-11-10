'''
'''
import dash_bootstrap_components as dbc
import logging
from dash import html

from app import app
from apps.investing_dash_components import style_center, get_investing_brstock_ticker_dbc

################ Logging information
logger = logging.getLogger(__name__)

################ APP LAYOUT
def investing_brstock_ticker_layout(ticker):
    logger.info("accessing investing_brstock_ticker app")
    app_layout = html.Center(html.Div([
        dbc.Row(
            html.H1(ticker)
        ),
        dbc.Row(
            html.Div(
                get_investing_brstock_ticker_dbc(ticker),
                style={"font-size":"13px"}
            ),
        )
    ],style=style_center))
    
    return app_layout
