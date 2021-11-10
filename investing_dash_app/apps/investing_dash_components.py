'''
'''
import dash_bootstrap_components as dbc
from lib.brstockmanager import BrStockManager

style_center = {
    "width":"1500px",
    "max-width":"1500px",
    "display":"inline-block",
    "margin-left":"auto",
    "margin-right":"auto"
}
style_update = {
    "width":"1500px",
    "max-width":"1500px",
    "display":"inline-block",
    "margin-left":"auto",
    "margin-right":"auto"
}
style_white = {
    "color": "white"
}

def get_operations_dbc():
    br_stock_manager = BrStockManager()
    br_stock_manager.load_brstock_operations_pkl()

    operations_table = dbc.Table.from_dataframe(
        br_stock_manager.dfop[["Broker", "Date", "Ticker", "Quantity", "Value", "Total Value",
            "Taxes", "IRRF", "Avg Value", "Profit"]].round(2),
        striped=True,
        bordered=True,
        hover=True,
        dark=True,
    )

    return operations_table

def get_investing_summary_dbc():
    br_stock_manager = BrStockManager()
    br_stock_manager.load_brstock_operations_pkl()

    summary_df = br_stock_manager.create_summary_by_date()

    summary_table = dbc.Table.from_dataframe(
        summary_df.reset_index().round(2),
        striped=True,
        bordered=True,
        hover=True,
        dark=True,
    )

    return summary_table

def get_investing_brstock_ticker_dbc(ticker):
    br_stock_manager = BrStockManager()
    br_stock_manager.load_brstock_operations_pkl()

    brstock_ticker_df = br_stock_manager.get_stock_by_ticker(ticker)

    brstock_ticker_table = dbc.Table.from_dataframe(
        brstock_ticker_df.reset_index().round(2),
        striped=True,
        bordered=True,
        hover=True,
        dark=True,
    )

    return brstock_ticker_table
