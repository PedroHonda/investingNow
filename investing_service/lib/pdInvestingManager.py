import os
import pandas as pd
import numpy as np

class pdInvestingManager:
    def __init__(self):
        self.cwd = os.getcwd()

    def createInvestingPD(self):
        # Values 
        header = ["Corretora", "Data", "Ticker", "Quantidade", "Valor", "Valor Total", "Taxas", "IRRF", "PM atual", "Lucro", "Comments"]
        header_type = ["str", "str", "str", "int", "float", "float", "float", "float", "float", "float", "str"]
        self.df = pd.DataFrame()
        for idx,h in enumerate(header):
            self.df[h] = pd.Series([], dtype=header_type[idx])

####################### considering to remove all of these...
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
        self.df["Data"] = pd.to_datetime(self.df["Data"], errors='coerce')
        self.df["Data"] = self.df["Data"].dt.date
        self.df["Quantidade"] = pd.to_numeric(self.df["Quantidade"], errors='coerce')
        self.df["Valor"] = pd.to_numeric(self.df["Valor"], errors='coerce')
        self.df["Taxas"] = pd.to_numeric(self.df["Taxas"], errors='coerce')
        self.df["IRRF"] = pd.to_numeric(self.df["IRRF"], errors='coerce')
        self.df["PM atual"] = pd.to_numeric(self.df["PM atual"], errors='coerce')
        self.df["Lucro"] = pd.to_numeric(self.df["Lucro"], errors='coerce')
####################### considering to remove all of these...

    def add_info(self, corretora="", data="", ticker="", valor=0.0, quantidade = 0, taxas=0.0, irrf=0.0, comentario=""):
        new_row = {"Corretora": corretora, "Data": data, "Ticker": ticker, "Quantidade": quantidade, "Valor": valor, "Taxas": taxas, "IRRF": irrf, "Comments": comentario}
        new_row["Valor Total"] = quantidade*valor
        new_row["PM atual"] = 0.0   # to be updated after updating data frame
        new_row["Lucro"] = 0.0      # TODO
        if quantidade < 0.0:
            currMeanValue = self.getCurrentMeanValueOfTicker(ticker)
            profit = (currMeanValue*quantidade)-(valor*quantidade)+taxas+irrf   # quantidade is negative
            new_row["Lucro"] = profit
        self.df = self.df.append(new_row, ignore_index=True)
        currMeanValue = self.getCurrentMeanValueOfTicker(ticker)
        self.df.at[self.df.index[-1], "PM atual"] = currMeanValue

    def getCurrentMeanValueOfTicker(self, ticker):
        flt = self.df["Ticker"].isin([ticker])
        d = self.df[flt]
        quant, value, taxes = d["Quantidade"], d["Valor"], d["Taxas"]
        currQuant, currTotalValue, currMeanValue = 0.0, 0.0, 0.0
        for i in quant.index:
            if quant.loc[i] > 0:
                currQuant += quant.loc[i]
                currTotalValue += value.loc[i]*quant.loc[i] + taxes.loc[i]
                currMeanValue = currTotalValue / currQuant
            else:
                currQuant += quant.loc[i]
                currTotalValue = currQuant * currMeanValue
                if not currQuant:
                    currMeanValue = 0.0
        return currMeanValue

    # TODO
    def getProfit(self):
        profit = 0.0
        if self.df:
            pass
        return profit

    def createSummary(self):
        """
        docstring
        """
        self.pt = pd.pivot_table(self.df, index=["Ticker"], values=["Quantidade"], aggfunc=np.sum)
        self.pt = self.pt[(self.pt.T != 0).any()]
        currPM = pd.pivot_table(self.df, index=["Ticker"], values=["PM atual"], aggfunc="last")
        currPM = currPM[(currPM.T != 0).any()]
        self.pt["PM atual"] = currPM["PM atual"]
