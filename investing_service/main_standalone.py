import json
from flask import Flask
from flask import render_template
from lib.pdInvestingManager import pdInvestingManager as PDIM
app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
