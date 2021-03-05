import os
import json
from flask import Flask, request, g
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from lib.pdInvestingManager import pdInvestingManager as PDIM

app = Flask(__name__)
api = Api(app)
CORS(app)

class Home(Resource):
    def get(self):
        im = PDIM()
        im.loadOperations_PKL()
        im_to_json = im.df.to_json(orient="split", index=False, date_format="iso")
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
            im.loadOperations_PKL()
        except:
            im.createInvestingPD()

        summaryDF = im.createSummaryByDate(im.now.strftime("%Y-%m-%d"))
        flt = summaryDF.isin([args['ticker']])

        if summaryDF[flt].empty and args["quantity"] < 0:
            return {'Conflict' : 'Request to sell a stock not previously owned'}, 409

        im.add_info(broker=args["broker"], date=args["date"], ticker=args["ticker"], 
                    value=args["value"], quantity=args["quantity"], taxes=args["taxes"], 
                    irrf=args["irrf"], comments=args["comments"], stock_class=args["stock_class"])

        im.saveOperations_PKL()
        im.saveOperations_CSV()

        return {'Success!' : args['ticker']}, 200

class Stock(Resource):
    def get(self, ticker):
        im = PDIM()
        im.loadOperations_PKL()
        flt = im.df["Ticker"].isin([ticker])
        tickerDF = im.df[flt]
        if tickerDF.empty:
            return "Not Found", 404
        tickerDF_to_json = tickerDF.to_json(orient="split", index=False, date_format="iso")
        return json.loads(tickerDF_to_json), 200


class Summary(Resource):
    def get(self):
        im = PDIM()
        im.loadOperations_PKL()
        im.createSummary()
        summaryDF = im.pt
        if summaryDF.empty:
            return "Not Found", 404
        summaryDF_to_json = summaryDF.to_json(orient="split", index=True, date_format="iso")
        return json.loads(summaryDF_to_json), 200

api.add_resource(Home, '/')
api.add_resource(Stock, '/<string:ticker>')
api.add_resource(Summary, '/summary')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)

