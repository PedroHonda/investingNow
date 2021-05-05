import os
import json
from flask import Flask, request, g
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from lib.brstockmanager import BrStockManager as PDIM

app = Flask(__name__)
api = Api(app)
CORS(app)

class Stock_Home(Resource):
    def get(self):
        im = PDIM()
        im.load_brstock_operations_pkl()
        im_to_json = im.dfop.to_json(orient="split", index=False, date_format="iso").replace("T00:00:00.000Z","")
        return json.loads(im_to_json), 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('broker', type=str, required=True, help='Broker must be a String')
        parser.add_argument('date', type=str, required=True, help='Date must be a String [YYYY-MM-DD]')
        parser.add_argument('ticker', type=str, required=True, help='Ticker must be a String')
        parser.add_argument('value', type=float, required=True, help='Value must be a Float')
        parser.add_argument('quantity', type=int, required=True, help='Quantity must be an Integer')
        parser.add_argument('taxes', type=float, help='Taxes must be a Float')
        parser.add_argument('stock_class', type=str, help='Stock Class must be a String')
        parser.add_argument('comments', type=str, help='Comments must be a String')
        try:
            args = parser.parse_args()      
        except:
            return {"Bad Input! Follow the example..." : {
                    "broker" : "Easynvest",
                    "date" : "2018-09-20",
                    "ticker" : "HGLG11",
                    "value" : 171.12,
                    "quantity" : 21,
                    "taxes" : 0.55,
                    "stock_class" : "FII",
                    "comments" : ""
                }}, 400

        if args['quantity'] > 0:
            args['irrf'] = 0.0
        else:
            args['irrf'] = float(args['quantity'])*args['value']*0.00005
        if not args['taxes']:
            args['taxes'] = 0.0
        if not args['stock_class']:
            args['stock_class'] = ''
        if not args['comments']:
            args['comments'] = ''

        im = PDIM()
        try:
            im.load_brstock_operations_pkl()
        except:
            im.create_brstock_dataframe()

        summaryDF = im.create_summary_by_date(im.now.strftime("%Y-%m-%d"))
        flt = summaryDF.isin([args['ticker']])

        if summaryDF[flt].empty and args["quantity"] < 0:
            return {'Conflict' : 'Request to sell a stock not previously owned'}, 409

        im.add_info(broker=args["broker"], date=args["date"], ticker=args["ticker"], 
                    value=args["value"], quantity=args["quantity"], taxes=args["taxes"], 
                    irrf=args["irrf"], comments=args["comments"], stock_class=args["stock_class"])

        im.save_brstock_operations_pkl()
        im.save_brstock_operations_csv()

        return {'Success!' : args['ticker']}, 200

class Stock_Ticker(Resource):
    def get(self, ticker):
        im = PDIM()
        im.load_brstock_operations_pkl()
        flt = im.dfop["Ticker"].isin([ticker])
        tickerDF = im.dfop[flt]
        if tickerDF.empty:
            return "Not Found", 404
        tickerDF_to_json = tickerDF.to_json(orient="split", index=False, date_format="iso").replace("T00:00:00.000Z","")
        return json.loads(tickerDF_to_json), 200


class Stock_Summary(Resource):
    def get(self):
        im = PDIM()
        im.load_brstock_operations_pkl()
        im.create_summary()
        summaryDF = im.summary_table
        if summaryDF.empty:
            return "Not Found", 404
        summaryDF_to_json = summaryDF.to_json(orient="split", index=True, date_format="iso").replace("T00:00:00.000Z","")
        return json.loads(summaryDF_to_json), 200

class Stock_Current(Resource):
    def get(self):
        im = PDIM()
        im.load_brstock_operations_pkl()
        currentDF = im.create_summary_by_date()
        if currentDF.empty:
            return "Not Found", 404
        currentDF_to_json = currentDF.to_json(orient="split", index=True, date_format="iso").replace("T00:00:00.000Z","")
        return json.loads(currentDF_to_json), 200

class Stock_Info(Resource):
    def get(self):
        im = PDIM()
        im.load_brstock_operations_pkl()
        brokers = im.dfop["Broker"].unique().tolist()
        classes = im.dfop["Class"].dropna().unique().tolist()
        if not brokers and not classes:
            return "Not Found", 404
        return {"brokers":brokers, "classes":classes}, 200   

api.add_resource(Stock_Home, '/stock/')
api.add_resource(Stock_Ticker, '/stock/<string:ticker>')
api.add_resource(Stock_Summary, '/stock/summary')
api.add_resource(Stock_Current, '/stock/current')
api.add_resource(Stock_Info, '/stock/info')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)

