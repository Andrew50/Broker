from flask import Blueprint, render_template, request, redirect, url_for
import sys
import os
import sys
src = os.path.dirname(os.path.abspath(__file__))
parent = src.split('Stocks2')[0]
sys.path.append(parent + (r'Stocks2/'))
from backend.Match import Match

admin = "dog1"
adminpswd = "dog1"
data_in = None
views = Blueprint(__name__, "views")

@views.route("/", methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["usr"]
        pswd = request.form["password"]
        if user == admin and pswd == adminpswd:
            return redirect(url_for("views.home"))
        else:
            return render_template("index.html")
    else:
        return render_template("index.html")

@views.route("/home", methods = ["POST", "GET"])
def home():
    if request.method == "POST":
        data_in = [request.form["ticker"],request.form["dt"],request.form["timeframe"]]
        if "" in data_in:
            return render_template("index2.html")
        else:
            global data_out
            data_out = Match.compute(data_in)
            print(data_out)
            return redirect(url_for("views.Return"))
    else:
        return render_template("index2.html")
    
@views.route("/return")
def Return():
    return render_template("index3.html", data = data_out, header = ['Score','Ticker','Datetime'])