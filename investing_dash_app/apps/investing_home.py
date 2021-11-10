'''
'''
import dash
import dash_bootstrap_components as dbc
import logging
from dash import html
from dash.dependencies import Input, Output, State

from lib.brstockmanager import BrStockManager
from app import app
from apps.investing_dash_components import style_center, style_white, get_operations_dbc

################ Logging information
logger = logging.getLogger(__name__)

################ APP LAYOUT
app_layout = html.Center(html.Div([
# INPUT DATA
    dbc.Card([
        dbc.CardHeader("ADD INFO", className="card-body"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(
                    dbc.InputGroup([
                        dbc.InputGroup("Broker"),
                        dbc.Input(placeholder="(required)", id='broker', style=style_white),
                    ]),
                ),
                dbc.Col(
                    dbc.InputGroup([
                        dbc.InputGroup("Data"),
                        dbc.Input(placeholder="YYYY-MM-DD", id='date', style=style_white),
                    ]),
                ),
            ]),
            dbc.Row([
                dbc.Col(
                    dbc.InputGroup([
                        dbc.InputGroup("Ticker"),
                        dbc.Input(placeholder="(required)", id='ticker', style=style_white),
                    ]),
                ),
                dbc.Col(
                    dbc.InputGroup([
                        dbc.InputGroup("Quantity"),
                        dbc.Input(placeholder="(negative for Selling)",
                                id='quantity',
                                style=style_white),
                    ]),
                ),
                dbc.Col(
                    dbc.InputGroup([
                        dbc.InputGroup("Value"),
                        dbc.Input(placeholder="(float)", id='value', style=style_white),
                    ]),
                ),
                dbc.Col(
                    dbc.InputGroup([
                        dbc.InputGroup("Taxes"),
                        dbc.Input(placeholder="(float)", id='taxes', style=style_white),
                    ]),
                ),
                dbc.Col(
                    dbc.InputGroup([
                        dbc.InputGroup("IRRF"),
                        dbc.Input(placeholder="(float)", id='irrf', style=style_white),
                    ]),
                ),
            ]),
            dbc.Row([
                dbc.Col(
                    dbc.InputGroup([
                        dbc.InputGroup("Class"),
                        dbc.Input(placeholder="(optional)", id='class', style=style_white),
                    ]),
                ),
                dbc.Col(
                    dbc.InputGroup([
                        dbc.InputGroup("Comment"),
                        dbc.Input(placeholder="(optional)", id='comment', style=style_white),
                    ]),
                ),
            ]),
            html.Br(),
            dbc.Row(
                dbc.Button("REGISTER",
                            id="register",
                            color="primary",
                            className="mr-1"
                )
            )
        ]),
    ]),
    html.Br(),
# OPERATIONS TABLE
    dbc.Row(
        html.Div(
            get_operations_dbc(),
            id="operations-table",
            style={"font-size":"13px"}
        ),
    )
],style=style_center))

################ CALLBACK DEFINITION
@app.callback(
    [
        Output("operations-table", "children"),
    ],
    [
        Input('register', 'n_clicks'),
    ],
    [
        State('broker', 'value'),
        State('date', 'value'),
        State('ticker', 'value'),
        State('quantity', 'value'),
        State('value', 'value'),
        State('taxes', 'value'),
        State('irrf', 'value'),
        State('class', 'value'),
        State('comment', 'value'),
    ]
)
def register_info(register_n, broker, date, ticker, quantity, value, taxes, irrf,
        stock_class, comment):
    if register_n is not None:
        logger.info("Registering new info: broker %s, date %s, ticker %s, quantity %s, value %s",
            broker, date, ticker, quantity, value)
        logger.info("taxes %s, irrf %s, stock_class %s, comment %s",
            taxes, irrf, stock_class, comment)
        # Do nothing if any of the required values are not filled
        if [x for x in (broker, date, ticker, quantity, value) if x is None]:
            logger.info("Some of the required values are not filled! Returning...")
            return dash.no_update

        if not taxes: taxes = 0.0
        if not irrf: irrf = 0.0
        if not comment: comment = ""
        if not stock_class: stock_class = ""

        # Adding info
        br_stock_manager = BrStockManager()
        br_stock_manager.load_brstock_operations_pkl()
        br_stock_manager.add_info(broker=broker, date=date, ticker=ticker, value=float(value),
            quantity=int(quantity), taxes=float(taxes), irrf=float(irrf), comments=comment,
            stock_class=stock_class)

        br_stock_manager.save_brstock_operations_pkl()
        br_stock_manager.save_brstock_operations_csv()

        return (get_operations_dbc(),)

    return dash.no_update
