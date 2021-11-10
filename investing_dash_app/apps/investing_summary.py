'''
'''
import dash_bootstrap_components as dbc
import logging
from dash import html

from app import app
from apps.investing_dash_components import style_center, get_investing_summary_dbc

################ Logging information
logger = logging.getLogger(__name__)

################ APP LAYOUT
def investing_summary_layout():
    logger.info("accessing investing_summary app")
    app_layout = html.Center(html.Div([
    # OPERATIONS TABLE
        dbc.Row(
            html.Div(
                get_investing_summary_dbc(),
                style={"font-size":"13px"}
            ),
        )
    ],style=style_center))
    
    return app_layout
