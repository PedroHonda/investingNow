from flask import Flask
from flask import render_template
from lib.pdInvestingManager import pdInvestingManager as PDIM
app = Flask(__name__)

@app.route('/')
def index():
    im = PDIM()
    im.loadOperations_PKL()
    return render_template("table.html", tables=[im.df.to_html()])
    #return render_template('indexTemplate.html')

@app.route('/<ticker>')
def stock(ticker):
    im = PDIM()
    im.loadOperations_PKL()
    return render_template("table.html", tables=[im.getStockByTicker_HTML(ticker)])
    #return render_template('carTemplate.html', APIipAddressPort="127.0.0.1:8080", carName=carName, OWNipAddressPort="127.0.0.1:7000")

@app.route('/summary')
def summary():
    im = PDIM()
    im.loadOperations_PKL()
    im.createSummary()
    return render_template("table.html", tables=[im.pt.to_html()])

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)
