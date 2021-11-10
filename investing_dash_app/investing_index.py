import logging
import time
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output

from app import app
from apps import investing_home as app_home
from apps.investing_summary import investing_summary_layout
from apps.investing_brstock_ticker import investing_brstock_ticker_layout

# Logging information
TIME_TAG = time.strftime("%Y_%m_%d-%H_%M_%S")
# logName = "./logs/investing_index_" + TIME_TAG + ".log"
logName = "./logs/investing_index.log"
logging.basicConfig(filename=logName,
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname).1s\t\t%(filename)s[%(lineno)d] : %(message)s',
    datefmt='%d-%m-%y %H:%M:%S',
    filemode='a')

app.title = "Investing Control"

app.layout = html.Div([
    dbc.Row([
        dbc.Navbar(
            html.Div([
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(dbc.NavbarBrand("Investing Control", className="ml-2")),
                        dbc.Col(dbc.NavLink("Home", href="/", className="nav-link")),
                        dbc.Col(dbc.NavLink("Summary", href="/summary", className="nav-link")),
                        dbc.Col(html.A(html.I("Github",className="fa fa-github"),className="nav-link")),
                    ],
                    align="center",
                ),
                href="https://github.com/PedroHonda/investingNow",
                className="navbar-brand",
            ),
        ], className="container-fluid"),
        color="bg-primary",
        className="navbar navbar-expand-lg navbar-dark bg-primary"
        )
    ]),
    html.Br(),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/winrate':
        return app_home.app_layout
    elif '/brstock/' in pathname:
        brstock = pathname.split("/brstock/")[1]
        return investing_brstock_ticker_layout(brstock)
    elif '/summary' in pathname:
        return investing_summary_layout()
    else:
        return app_home.app_layout

if __name__ == '__main__':
    app.run_server(debug=True, port="8080")
