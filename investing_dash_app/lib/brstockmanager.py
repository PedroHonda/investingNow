'''
Class BrStockManager:
- Manages Brazilian stock/FII operations
- Create reports
- Analyze information
'''
import datetime
import logging
import os
import pandas as pd
import numpy as np
from pandas_datareader import data as web

logger = logging.getLogger(__name__)

class BrStockManager:
    '''
    Manager for Brazilian Stock and FII operations
    '''
    def __init__(self):
        self.cwd = os.getcwd()
        self.now = datetime.datetime.now()
        self.dfop = pd.DataFrame()
        self.summary_table = pd.DataFrame()
        logger.info("BrStockManager class created")

    def create_brstock_dataframe(self):
        '''
        Create operations dataframe from scratch
        '''
        logger.info("BrStockManager - create_brstock_dataframe")
        headers = ["Broker", "Date", "Ticker", "Quantity",
            "Value", "Total Value", "Taxes", "IRRF",
            "Avg Value", "Profit", "Comments"]
        header_type = ["str", "str", "str", "int", "float",
            "float", "float", "float", "float", "float", "str"]
        for idx,header in enumerate(headers):
            self.dfop[header] = pd.Series([], dtype=header_type[idx])

    def save_brstock_operations_pkl(self):
        '''
        Save operations dataframe in pickle format
        '''
        logger.info("BrStockManager - save_brstock_operations_pkl")
        if not self.dfop.empty:
            # save as .pkl
            self.dfop.to_pickle(os.path.join(self.cwd, "pd_raw_data", "operations.pkl"))

    def load_brstock_operations_pkl(self):
        '''
        Load operations dataframe from pickle file
        '''
        logger.info("BrStockManager - load_brstock_operations_pkl")
        self.dfop = pd.read_pickle(os.path.join(self.cwd, "pd_raw_data", "operations.pkl"))

    def save_brstock_operations_csv(self):
        '''
        Save operations dataframe in csv format
        '''
        logger.info("BrStockManager - save_brstock_operations_csv")
        if not self.dfop.empty:
            # save as .csv
            self.dfop.to_csv(os.path.join(self.cwd,
                "pd_raw_data", "operations.csv"), index=False, sep=';')

    def load_brstock_operations_csv(self):
        '''
        Load operations dataframe from csv file
        '''
        logger.info("BrStockManager - load_brstock_operations_csv")
        self.dfop = pd.read_csv(os.path.join(self.cwd, "pd_raw_data", "operations.csv"), sep=';')
        self.dfop["Date"] = pd.to_datetime(self.dfop["Date"], errors='coerce', format="%Y-%m-%d")
        self.dfop["Date"] = self.dfop["Date"].dt.date
        self.dfop["Quantity"] = pd.to_numeric(self.dfop["Quantity"], errors='coerce')
        self.dfop["Value"] = pd.to_numeric(self.dfop["Value"], errors='coerce')
        self.dfop["Total Value"] = pd.to_numeric(self.dfop["Total Value"], errors='coerce')
        self.dfop["Taxes"] = pd.to_numeric(self.dfop["Taxes"], errors='coerce')
        self.dfop["IRRF"] = pd.to_numeric(self.dfop["IRRF"], errors='coerce')
        self.dfop["Avg Value"] = pd.to_numeric(self.dfop["Avg Value"], errors='coerce')
        self.dfop["Profit"] = pd.to_numeric(self.dfop["Profit"], errors='coerce')

    def add_info(self, **kwargs):
        '''
        Add a row into current dfop (operations dataframe)
        Mandatory inputs in kwargs:
        - broker
        - date
        - ticker
        - value
        - quantity
        Optional inputs in kwargs:
        - taxes
        - irrf
        - comments
        - stock_class
        '''
        logger.info("BrStockManager - add_info - kwargs %s", kwargs)
        broker = kwargs["broker"]
        ticker = kwargs["ticker"]
        date = kwargs["date"]
        value = kwargs["value"]
        quantity = kwargs["quantity"]
        taxes = kwargs.get("taxes", 0.0)
        irrf = kwargs.get("irrf", 0.0)
        comments = kwargs.get("comments", "")
        stock_class = kwargs.get("stock_class", "")
        new_row = {"Broker": broker, "Ticker": ticker, "Quantity": quantity,
            "Value": value, "Taxes": taxes, "IRRF": irrf,
            "Comments": comments, "Class": stock_class}
        new_row["Date"] = pd.to_datetime(date, errors='coerce', format="%Y-%m-%d").date()
        new_row["Total Value"] = quantity*value
        new_row["Avg Value"] = 0.0   # to be updated after updating data frame
        new_row["Profit"] = np.NaN
        if quantity < 0.0:
            curr_avg_value = self.get_current_avgvalue_of_ticker(ticker)
            profit = (curr_avg_value*quantity)-(value*quantity)+taxes+irrf   # quantity is negative
            new_row["Profit"] = profit
        self.dfop = self.dfop.append(new_row, ignore_index=True)
        curr_avg_value = self.get_current_avgvalue_of_ticker(ticker)
        self.dfop.at[self.dfop.index[-1], "Avg Value"] = curr_avg_value

    def get_current_avgvalue_of_ticker(self, ticker):
        '''
        Given a ticker as input, calculate current Average value
        '''
        logger.info("BrStockManager - get_current_avgvalue_of_ticker - ticker %s", ticker)
        flt = self.dfop["Ticker"].isin([ticker])
        dft = self.dfop[flt]
        quant, value, taxes = dft["Quantity"], dft["Value"], dft["Taxes"]
        curr_quant, curr_total_value, curr_avg_value = 0.0, 0.0, 0.0
        for i in quant.index:
            if quant.loc[i] > 0:
                curr_quant += quant.loc[i]
                curr_total_value += value.loc[i]*quant.loc[i] + taxes.loc[i]
                curr_avg_value = curr_total_value / curr_quant
            else:
                curr_quant += quant.loc[i]
                curr_total_value = curr_quant * curr_avg_value
                if not curr_quant:
                    curr_avg_value = 0.0
        return curr_avg_value

    def create_summary(self):
        '''
        Create a summary using current date
        '''
        logger.info("BrStockManager - create_summary")
        self.summary_table = self.create_summary_by_date(date=self.now.strftime("%Y-%m-%d"),
            get_last_price=True)

    def snapshot_summary(self):
        '''
        Creates a csv snapshot for the current position
        '''
        logger.info("BrStockManager - snapshot_summary")
        if not self.summary_table.empty:
            self.summary_table.to_csv(os.path.join(self.cwd, "pd_raw_data",
                self.now.strftime("%Y-%m-%d")+"_Summary_Snapshot.csv"), sep=';')

    def create_summary_by_date(self, date="", get_last_price=False):
        '''
        Create a summary using the date provided in the input
        '''
        logger.info("BrStockManager - create_summary_by_date - date %s, get_last_price %s",
            date, get_last_price)
        if not date:
            date = self.now.strftime("%Y-%m-%d")
        summary_df = pd.DataFrame()
        pd_date = pd.to_datetime(date, errors='coerce', format="%Y-%m-%d")
        if not self.dfop.empty and not pd.isnull(pd_date):
            flt = self.dfop["Date"] < pd_date
            summary_df = pd.pivot_table(self.dfop[flt], index=["Ticker"],
                values=["Quantity"], aggfunc=np.sum)
            summary_df = summary_df[(summary_df.T != 0).any()]
            curr_avg = pd.pivot_table(self.dfop[flt], index=["Ticker"],
                values=["Avg Value"], aggfunc="last")
            curr_avg = curr_avg[(curr_avg.T != 0).any()]
            summary_df["Avg Value"] = curr_avg["Avg Value"]
            summary_df["Total"] = summary_df["Avg Value"]*summary_df["Quantity"]

            if get_last_price:
                delta_5 = datetime.timedelta(5) # delta of 5 days
                start = (datetime.datetime.strptime(date, '%Y-%m-%d')-delta_5).strftime("%m-%d-%Y")
                end = (datetime.datetime.strptime(date, '%Y-%m-%d')).strftime("%m-%d-%Y")
                tickers = [s + ".SA" for s in summary_df.index.tolist()]
                dft = web.DataReader(tickers, data_source='yahoo', start=start, end=end)
                summary_df["Last Price"] = dft["Close"].iloc[-1].tolist()
                summary_df["Current Position"] = summary_df["Last Price"]*summary_df["Quantity"]
                summary_df["Delta"] = (summary_df["Last Price"]-
                    summary_df["Avg Value"])*summary_df["Quantity"]
        return summary_df

    def get_stock_by_ticker(self, ticker):
        '''
        Returns all operations for a given stock in HTML format
        '''
        logger.info("BrStockManager - get_stock_by_ticker - ticker %s", ticker)
        flt = self.dfop["Ticker"].isin([ticker])
        stock = self.dfop[flt]
        return stock

    def get_stock_by_ticker_html(self, ticker):
        '''
        Returns all operations for a given stock in HTML format
        '''
        logger.info("BrStockManager - get_stock_by_ticker_html - ticker %s", ticker)
        flt = self.dfop["Ticker"].isin([ticker])
        stock = self.dfop[flt]
        return stock.to_html()
