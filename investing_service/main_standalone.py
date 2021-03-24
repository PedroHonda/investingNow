import json
from flask import Flask, request, g
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from flask import render_template
from lib.pdInvestingManager import pdInvestingManager as PDIM

app = Flask(__name__)
api = Api(app)
CORS(app)

@app.route('/')
def index():
    im = PDIM()
    im.loadOperations_PKL()
    return render_template("table_generic.html", tables=[im.df.to_html()])
    #return render_template('indexTemplate.html')

@app.route('/<ticker>')
def stock(ticker):
    im = PDIM()
    im.loadOperations_PKL()
    return render_template("table_generic.html", tables=[im.getStockByTicker_HTML(ticker)])
    #return render_template('carTemplate.html', APIipAddressPort="127.0.0.1:8080", carName=carName, OWNipAddressPort="127.0.0.1:7000")

@app.route('/summary')
def summary():
    im = PDIM()
    im.loadOperations_PKL()
    im.createSummary()
    return render_template("table_generic.html", tables=[im.pt.to_html()])

@app.route('/view')
def view():
    im = PDIM()
    im.loadOperations_PKL()
    brokers = im.df["Broker"].unique().tolist()
    classes = im.df["Class"].dropna().unique().tolist()
    return render_template("index.html", brokers=brokers, classes=classes)

@app.route('/view/stock')
def view_stock():
    im = PDIM()
    im.loadOperations_PKL()
    im_to_json = im.df.to_json(orient="split", index=False, date_format="iso").replace("T00:00:00.000Z","")
    r = json.loads(im_to_json)
    brokers = im.df["Broker"].unique().tolist()
    classes = im.df["Class"].dropna().unique().tolist()
    return render_template("stock_main.html", heading='Stock', columns=r["columns"], rows=r["data"], brokers=brokers, classes=classes)

@app.route('/view/stock/<ticker>')
def view_stock_ticker(ticker):
    im = PDIM()
    im.loadOperations_PKL()
    flt = im.df["Ticker"].isin([ticker])
    tickerDF = im.df[flt]
    if tickerDF.empty:
        return render_template("stock_ticker.html", heading=ticker, columns=["Not Found"], rows=[""])
    tickerDF_to_json = tickerDF.to_json(orient="split", index=False, date_format="iso").replace("T00:00:00.000Z","")
    r = json.loads(tickerDF_to_json)
    return render_template("stock_ticker.html", heading=ticker, columns=r["columns"], rows=r["data"])

@app.route('/view/stock/current')
def view_stock_current():
    im = PDIM()
    im.loadOperations_PKL()
    currentDF = im.createSummaryByDate()
    if currentDF.empty:
        return render_template("stock_ticker.html", heading="Current", columns=["Null"], rows=[""])
    currentDF_to_json = currentDF.to_json(orient="split", index=True, date_format="iso").replace("T00:00:00.000Z","")
    r = json.loads(currentDF_to_json)
    z = zip(r["index"], r["data"])
    return render_template("simple_table_with_index.html", heading="Current", columns=r["columns"], rows=r["data"], z=z)

@app.route('/view/stock/current/detail')
def view_stock_current_detail():
    im = PDIM()
    im.loadOperations_PKL()
    im.createSummary()
    summaryDF = im.pt
    if summaryDF.empty:
        return render_template("stock_ticker.html", heading="Summary - Details", columns=["Null"], rows=[""])
    summaryDF_to_json = summaryDF.to_json(orient="split", index=True, date_format="iso").replace("T00:00:00.000Z","")
    r = json.loads(summaryDF_to_json)
    z = zip(r["index"], r["data"])
    return render_template("simple_table_with_index.html", heading="Summary - Details", columns=r["columns"], rows=r["data"], z=z)


class Stock_Home(Resource):
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
            pass
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
            args['irrf'] = -float(args['quantity'])*float(args['value'])*0.00005
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

api.add_resource(Stock_Home, '/stock/')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
