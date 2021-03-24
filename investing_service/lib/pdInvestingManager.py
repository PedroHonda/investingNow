import os
import pandas as pd
import numpy as np
import datetime
import re
from pandas_datareader import data as web

class pdInvestingManager:
    def __init__(self):
        self.cwd = os.getcwd()
        self.now = datetime.datetime.now()

    def createInvestingPD(self):
        header = ["Broker", "Date", "Ticker", "Quantity", "Value", "Total Value", "Taxes", "IRRF", "Avg Value", "Profit", "Comments"]
        header_type = ["str", "str", "str", "int", "float", "float", "float", "float", "float", "float", "str"]
        self.df = pd.DataFrame()
        for idx,h in enumerate(header):
            self.df[h] = pd.Series([], dtype=header_type[idx])

    def saveOperations_PKL(self):
        if not self.df.empty:
            self.df.to_pickle(os.path.join(self.cwd, "pdRawData", "operations.pkl"))  # save as .pkl
    
    def loadOperations_PKL(self):
        self.df = pd.read_pickle(os.path.join(self.cwd, "pdRawData", "operations.pkl"))

    def saveOperations_CSV(self):
        if not self.df.empty:
            self.df.to_csv(os.path.join(self.cwd, "pdRawData", "operations.csv"), index=False, sep=';')  # save as .csv

    def loadOperations_CSV(self):
        self.df = pd.read_csv(os.path.join(self.cwd, "pdRawData", "operations.csv"), sep=';')
        self.df["Date"] = pd.to_datetime(self.df["Date"], errors='coerce', format="%Y-%m-%d")
        self.df["Date"] = self.df["Date"].dt.date
        self.df["Quantity"] = pd.to_numeric(self.df["Quantity"], errors='coerce')
        self.df["Value"] = pd.to_numeric(self.df["Value"], errors='coerce')
        self.df["Total Value"] = pd.to_numeric(self.df["Total Value"], errors='coerce')
        self.df["Taxes"] = pd.to_numeric(self.df["Taxes"], errors='coerce')
        self.df["IRRF"] = pd.to_numeric(self.df["IRRF"], errors='coerce')
        self.df["Avg Value"] = pd.to_numeric(self.df["Avg Value"], errors='coerce')
        self.df["Profit"] = pd.to_numeric(self.df["Profit"], errors='coerce')

    def add_info(self, broker="", date="", ticker="", value=0.0, quantity = 0, taxes=0.0, irrf=0.0, comments="", stock_class=""):
        new_row = {"Broker": broker, "Ticker": ticker, "Quantity": quantity, "Value": value, "Taxes": taxes, "IRRF": irrf, "Comments": comments, "Class": stock_class}
        new_row["Date"] = pd.to_datetime(date, errors='coerce', format="%Y-%m-%d").date()
        new_row["Total Value"] = quantity*value
        new_row["Avg Value"] = 0.0   # to be updated after updating data frame
        new_row["Profit"] = np.NaN
        if quantity < 0.0:
            currAvgValue = self.getCurrentAvgValueOfTicker(ticker)
            profit = (currAvgValue*quantity)-(value*quantity)+taxes+irrf   # quantity is negative
            new_row["Profit"] = profit
        self.df = self.df.append(new_row, ignore_index=True)
        currAvgValue = self.getCurrentAvgValueOfTicker(ticker)
        self.df.at[self.df.index[-1], "Avg Value"] = currAvgValue

    def getCurrentAvgValueOfTicker(self, ticker):
        flt = self.df["Ticker"].isin([ticker])
        d = self.df[flt]
        quant, value, taxes = d["Quantity"], d["Value"], d["Taxes"]
        currQuant, currTotalValue, currAvgValue = 0.0, 0.0, 0.0
        for i in quant.index:
            if quant.loc[i] > 0:
                currQuant += quant.loc[i]
                currTotalValue += value.loc[i]*quant.loc[i] + taxes.loc[i]
                currAvgValue = currTotalValue / currQuant
            else:
                currQuant += quant.loc[i]
                currTotalValue = currQuant * currAvgValue
                if not currQuant:
                    currAvgValue = 0.0
        return currAvgValue

    def createSummary(self):
        self.pt = self.createSummaryByDate(date=self.now.strftime("%Y-%m-%d"), getLastPrice=True)

    def snapshotSummary(self):
        if not self.pt.empty:
            self.pt.to_csv(os.path.join(self.cwd, "pdRawData", self.now.strftime("%Y-%m-%d")+"_Summary_Snapshot.csv"), sep=';')

    def createSummaryByDate(self, date="", getLastPrice=False):
        if not date:
            date = self.now.strftime("%Y-%m-%d")
        summaryDF = pd.DataFrame()
        pd_date = pd.to_datetime(date, errors='coerce', format="%Y-%m-%d")
        if not self.df.empty and not pd.isnull(pd_date):
            flt = self.df["Date"] < pd_date
            summaryDF = pd.pivot_table(self.df[flt], index=["Ticker"], values=["Quantity"], aggfunc=np.sum)
            summaryDF = summaryDF[(summaryDF.T != 0).any()]
            currAV = pd.pivot_table(self.df[flt], index=["Ticker"], values=["Avg Value"], aggfunc="last")
            currAV = currAV[(currAV.T != 0).any()]
            summaryDF["Avg Value"] = currAV["Avg Value"]
            summaryDF["Total"] = summaryDF["Avg Value"]*summaryDF["Quantity"]
            
            if getLastPrice:
                delta_5 = datetime.timedelta(5) # delta of 5 days
                start = (datetime.datetime.strptime(date, '%Y-%m-%d')-delta_5).strftime("%m-%d-%Y")
                end = (datetime.datetime.strptime(date, '%Y-%m-%d')).strftime("%m-%d-%Y")
                tickers = [s + ".SA" for s in summaryDF.index.tolist()]
                df = web.DataReader(tickers, data_source='yahoo', start=start, end=end)
                summaryDF["Last Price"] = df["Close"].iloc[-1].tolist()
                summaryDF["Current Position"] = summaryDF["Last Price"]*summaryDF["Quantity"]
                summaryDF["Delta"] = (summaryDF["Last Price"]-summaryDF["Avg Value"])*summaryDF["Quantity"]
        return summaryDF

    def getStockByTicker_HTML(self, ticker):
        flt = self.df["Ticker"].isin([ticker])
        stock = self.df[flt]
        return stock.to_html()
