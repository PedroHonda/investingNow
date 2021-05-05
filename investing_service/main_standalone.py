'''
Exposes investing service web pages and REST API
'''
import json
from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from lib.brstockmanager import BrStockManager as BRSM

app = Flask(__name__)
api = Api(app)
CORS(app)

@app.route('/')
def index():
    '''
    Generic HTML page with all operations from BrStockManager
    '''
    brstock = BRSM()
    brstock.load_brstock_operations_pkl()
    return render_template("table_generic.html", tables=[brstock.dfop.to_html()])
    #return render_template('indexTemplate.html')

@app.route('/<ticker>')
def stock(ticker):
    '''
    Generic HTML page with operations for a stock by ticker
    '''
    brstock = BRSM()
    brstock.load_brstock_operations_pkl()
    return render_template("table_generic.html", tables=[brstock.get_stock_by_ticker_html(ticker)])
    #return render_template('carTemplate.html',
    # APIipAddressPort="127.0.0.1:8080", carName=carName,
    # OWNipAddressPort="127.0.0.1:7000")

@app.route('/summary')
def summary():
    '''
    Generic Summary HTML page
    '''
    brstock = BRSM()
    brstock.load_brstock_operations_pkl()
    brstock.create_summary()
    return render_template("table_generic.html", tables=[brstock.summary_table.to_html()])

@app.route('/view')
def view():
    '''
    Index HTML page
    '''
    brstock = BRSM()
    brstock.load_brstock_operations_pkl()
    brokers = brstock.dfop["Broker"].unique().tolist()
    classes = brstock.dfop["Class"].dropna().unique().tolist()
    return render_template("index.html", brokers=brokers, classes=classes)

@app.route('/view/stock')
def view_stock():
    '''
    HTML page with all BR market operations
    '''
    brstock = BRSM()
    brstock.load_brstock_operations_pkl()
    brstock_to_json = brstock.dfop.to_json(orient="split", index=False,
        date_format="iso").replace("T00:00:00.000Z","")
    raw = json.loads(brstock_to_json)
    brokers = brstock.dfop["Broker"].unique().tolist()
    classes = brstock.dfop["Class"].dropna().unique().tolist()
    return render_template("stock_main.html", heading='Stock', columns=raw["columns"],
        rows=raw["data"], brokers=brokers, classes=classes)

@app.route('/view/stock/<ticker>')
def view_stock_ticker(ticker):
    '''
    HTML page with all BR market operations for a ticker
    '''
    brstock = BRSM()
    brstock.load_brstock_operations_pkl()
    flt = brstock.dfop["Ticker"].isin([ticker])
    ticker_df = brstock.dfop[flt]
    if ticker_df.empty:
        return render_template("stock_ticker.html", heading=ticker,
            columns=["Not Found"], rows=[""])
    ticker_df_to_json = ticker_df.to_json(orient="split", index=False,
        date_format="iso").replace("T00:00:00.000Z","")
    raw = json.loads(ticker_df_to_json)
    return render_template("stock_ticker.html", heading=ticker,
        columns=raw["columns"], rows=raw["data"])

@app.route('/view/stock/current')
def view_stock_current():
    '''
    HTML page with a summary on current position
    '''
    brstock = BRSM()
    brstock.load_brstock_operations_pkl()
    current_df = brstock.create_summary_by_date()
    if current_df.empty:
        return render_template("stock_ticker.html", heading="Current", columns=["Null"], rows=[""])
    current_df_to_json = current_df.to_json(orient="split", index=True,
        date_format="iso").replace("T00:00:00.000Z","")
    raw = json.loads(current_df_to_json)
    zipped = zip(raw["index"], raw["data"])
    return render_template("simple_table_with_index.html", heading="Current",
        columns=raw["columns"], rows=raw["data"], z=zipped)

@app.route('/view/stock/current/detail')
def view_stock_current_detail():
    '''
    HTML page with detailed information on current position
    '''
    brstock = BRSM()
    brstock.load_brstock_operations_pkl()
    brstock.create_summary()
    summary_df = brstock.summary_table
    if summary_df.empty:
        return render_template("stock_ticker.html", heading="Summary - Details",
            columns=["Null"], rows=[""])
    summary_df_to_json = summary_df.to_json(orient="split", index=True,
        date_format="iso").replace("T00:00:00.000Z","")
    raw = json.loads(summary_df_to_json)
    zipped = zip(raw["index"], raw["data"])
    return render_template("simple_table_with_index.html",
        heading="Summary - Details", columns=raw["columns"], rows=raw["data"], z=zipped)


class StockHome(Resource):
    '''
    REST API for BR Stock
    '''
    def post(self):
        '''
        HTTP POST method
        '''
        parser = reqparse.RequestParser()
        parser.add_argument('broker',type=str,required=True,help='Broker must be a String')
        parser.add_argument('date',type=str,required=True,help='Date must be a String [YYYY-MM-DD]')
        parser.add_argument('ticker',type=str,required=True,help='Ticker must be a String')
        parser.add_argument('value',type=float,required=True,help='Value must be a Float')
        parser.add_argument('quantity',type=int,required=True,help='Quantity must be an Integer')
        parser.add_argument('taxes',type=float,help='Taxes must be a Float')
        parser.add_argument('stock_class',type=str,help='Stock Class must be a String')
        parser.add_argument('comments',type=str,help='Comments must be a String')
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
            args['irrf'] = -float(args['quantity'])*float(args['value'])*0.00005
        if not args['taxes']:
            args['taxes'] = 0.0
        if not args['stock_class']:
            args['stock_class'] = ''
        if not args['comments']:
            args['comments'] = ''
        brstock = BRSM()
        try:
            brstock.load_brstock_operations_pkl()
        except:
            brstock.create_brstock_dataframe()
        summary_df = brstock.create_summary_by_date(brstock.now.strftime("%Y-%m-%d"))
        flt = summary_df.isin([args['ticker']])
        if summary_df[flt].empty and args["quantity"] < 0:
            return {'Conflict' : 'Request to sell a stock not previously owned'}, 409

        brstock.add_info(broker=args["broker"], date=args["date"], ticker=args["ticker"],
                    value=args["value"], quantity=args["quantity"], taxes=args["taxes"],
                    irrf=args["irrf"], comments=args["comments"], stock_class=args["stock_class"])

        brstock.save_brstock_operations_pkl()
        brstock.save_brstock_operations_csv()

        return {'Success!' : args['ticker']}, 200

api.add_resource(StockHome, '/stock/')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
