# Standard libs
import os
import sys
import argparse
from lib.pdInvestingManager import pdInvestingManager as PDIM

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-insert', help='Use this option to manually insert a operation', action='store_true')
    parser.add_argument('-snap', help='Use this option to create a snapshot', action='store_true')
    parser.add_argument('-syncCSV', help='Use this option to sync current CSV to Pickle', action='store_true')
    args = parser.parse_args()

    im = PDIM()
    
    if args.syncCSV:
        im.loadOperations_CSV()
        im.saveOperations_PKL()
    else:
        im.loadOperations_PKL()
    if args.insert:
        broker = input("Broker : ")
        date = input("Date [YYYY-MM-DD] : ")
        ticker = input("Ticker : ")
        value = float(input("Value (float) : "))
        quantity = float(input("Quantity (negative for Selling) : "))
        taxes = float(input("Taxes : "))
        if quantity > 0.0:
            irrf = 0.0
        else:
            irrf = quantity*value*0.00005
        stock_class = input("Class : ")
        comments = input("Comments : ")
        im.add_info(broker=broker, date=date, ticker=ticker, value=value, quantity = quantity, taxes=taxes, irrf=irrf, comments=comments, stock_class=stock_class)
        im.saveOperations_PKL()
        im.saveOperations_CSV()
    if args.snap:
        im.createSummary()
        im.snapshotSummary()

if __name__ == "__main__":
    main()
    
