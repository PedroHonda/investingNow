'''
Class CryptoManager:
- Manages Crypto related operations
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

class CryptoManager:
    '''
    Manager for Crypto operations
    '''
    def __init__(self):
        self.cwd = os.getcwd()
        self.now = datetime.datetime.now()
        self.dfop = pd.DataFrame()
        self.summary_table = pd.DataFrame()
        logger.info("CryptoManager class created")

    def save_crypto_operations_pkl(self):
        '''
        Save operations dataframe in pickle format
        '''
        logger.info("CryptoManager - save_crypto_operations_pkl")
        if not self.dfop.empty:
            # save as .pkl
            self.dfop.to_pickle(os.path.join(self.cwd, "pd_raw_data", "crypto_operations.pkl"))

    def load_crypto_operations_pkl(self):
        '''
        Load operations dataframe from pickle file
        '''
        logger.info("CryptoManager - load_crypto_operations_pkl")
        self.dfop = pd.read_pickle(os.path.join(self.cwd, "pd_raw_data", "crypto_operations.pkl"))

    def save_crypto_operations_csv(self):
        '''
        Save operations dataframe in csv format
        '''
        logger.info("CryptoManager - save_crypto_operations_csv")
        if not self.dfop.empty:
            # save as .csv
            self.dfop.to_csv(os.path.join(self.cwd, "pd_raw_data", "crypto_operations.csv"),
                             index=False, sep=';')

    def add_info(self, **kwargs):
        '''
        Add a row into current dfop (operations dataframe)
        Mandatory inputs in kwargs:
        - exchange
        - date
        - ticker
        - price (reais)
        - quantity
        Optional inputs in kwargs:
        - comments
        '''
        logger.info("BrStockManager - add_info - kwargs %s", kwargs)
        broker = kwargs["broker"]
        ticker = kwargs["ticker"]
        date = kwargs["date"]
        price = kwargs["price"]
        quantity = kwargs["quantity"]
        comments = kwargs.get("comments", "")

        new_row = {"Broker": broker, "Ticker": ticker, "Quantity": quantity,
            "Price": price, "Comments": comments}
        new_row["Date"] = pd.to_datetime(date, errors='coerce', format="%Y-%m-%d").date()
        new_row["Crypto Value"] = price/quantity

        self.dfop = self.dfop.append(new_row, ignore_index=True)
