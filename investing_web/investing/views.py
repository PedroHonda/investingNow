import requests
from django.shortcuts import render

# Create your views here.
def mainPage_view(request, *args, **kwargs):
    r_info = requests.get("http://127.0.0.1:8080/stock/info")
    return render(request, "investing/index.html", {'brokers': r_info.json()["brokers"], "classes": r_info.json()["classes"]})

def settings_view(request, *args, **kwargs):
    return render(request, "investing/settings.html", {})

def stock_view(request, *args, **kwargs):
    r = requests.get("http://127.0.0.1:8080/stock")
    r_info = requests.get("http://127.0.0.1:8080/stock/info")
    return render(request, "investing/stock_main.html", {'heading': 'Stock', 'columns': r.json()["columns"], 'rows': r.json()["data"], 'brokers': r_info.json()["brokers"], "classes": r_info.json()["classes"]})

def stock_by_ticker_view(request, ticker, *args, **kwargs):
    r = requests.get("http://127.0.0.1:8080/stock/"+ticker)
    return render(request, "investing/stock_ticker.html", {'heading': ticker, 'columns': r.json()["columns"], 'rows': r.json()["data"]})

def stock_summary_current_view(request, *args, **kwargs):
    r = requests.get("http://127.0.0.1:8080/stock/current")
    z = zip(r.json()["index"], r.json()["data"])
    return render(request, "investing/simple_table_with_index.html", {'heading': 'Current', 'columns': r.json()["columns"], 'z':z})

def stock_summary_detail_view(request, *args, **kwargs):
    r = requests.get("http://127.0.0.1:8080/stock/summary")
    z = zip(r.json()["index"], r.json()["data"])
    return render(request, "investing/simple_table_with_index.html", {'heading': 'Summary', 'columns': r.json()["columns"], 'z':z})
