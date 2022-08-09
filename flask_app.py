from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
from datetime import datetime, timedelta


app = Flask(__name__)
app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="BDATProject",
    password="myExchangeRates",
    hostname="BDATProject.mysql.pythonanywhere-services.com",
    databasename="BDATProject$ExchangeRates",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

API_KEY = "P2dnLPUw5Pz0HyGerxzFhaJLb89sASMq"

class CurrenySymbols(db.Model):
    __tablename__ = "currencySymbols"
    curr = db.Column(db.String(5), primary_key=True)
    currName = db.Column(db.String(50))

class ExchangeRateRow(db.Model):
    __tablename__ = "exchangeRates"

    date = db.Column(db.Integer, primary_key=True)
    USD = db.Column(db.Float)
    CAD = db.Column(db.Float)
    INR = db.Column(db.Float)
    EUR = db.Column(db.Float)
    AED = db.Column(db.Float)
    BHD = db.Column(db.Float)
    HKD = db.Column(db.Float)
    JPY = db.Column(db.Float)
    Highest = db.Column(db.String(5))
    HighestValue = db.Column(db.Float)
    Lowest = db.Column(db.String(5))
    LowestValue = db.Column(db.Float)

@app.route("/initialize", methods=["GET"])
def initialize():

    db.drop_all()
    db.create_all()
    url = "https://api.apilayer.com/exchangerates_data/symbols"

    payload = {}
    headers= {
    "apikey": API_KEY
    }

    result = {}
    try:
        response = requests.get(url, headers=headers, data = payload)
        if response.status_code == 200:
            result = response.json()
        else:
            return("The api throwed the following error:", response.status_code)

    except requests.exceptions.HTTPError as e:
            return("The code encountered the following HTTPError error:", e)
    except requests.exceptions.RequestException as e:
        return("The code encountered the following RequestException error:", e)
    except Exception as e:
        return("The code encountered the following error:", e)

    for curr,currencyName in result.get("symbols", {}).items():
        currObj = CurrenySymbols(curr=curr,currName=currencyName)
        db.session.add(currObj)
    
    db.session.commit()

    endDateTimeObj = datetime.today()
    startDateTimeObj = datetime.today() - timedelta(days=30)

    end_date = endDateTimeObj.strftime("%Y-%m-%d")
    start_date = startDateTimeObj.strftime("%Y-%m-%d")

    url = url = f"https://api.apilayer.com/exchangerates_data/timeseries?start_date={start_date}&end_date={end_date}"

    payload = {}
    headers= {
    "apikey": API_KEY
    }

    result = {}
    try:
        response = requests.get(url, headers=headers, data = payload)
        if response.status_code == 200:
            result = response.json()
        else:
            return("The api throwed the following error:", response.status_code)

    except requests.exceptions.HTTPError as e:
            return("The code encountered the following HTTPError error:", e)
    except requests.exceptions.RequestException as e:
        return("The code encountered the following RequestException error:", e)
    except Exception as e:
        return("The code encountered the following error:", e)

    for strDate,values in result.get("rates", {}).items():
        usd = values.get("USD", 0)
        cad = values.get("CAD", 0)
        inr = values.get("INR", 0)
        eur = values.get("EUR", 0)
        aed = values.get("AED", 0)
        bhd = values.get("BHD", 0)
        hkd = values.get("HKD", 0)
        jpy = values.get("JPY", 0)
        date = strDate.replace("-", "")
        currExchangeRateObj = ExchangeRateRow(
            date=date, USD=usd, CAD=cad, INR=inr, EUR=eur, AED=aed, BHD=bhd, HKD=hkd, JPY=jpy
        )
        db.session.add(currExchangeRateObj)
    
    db.session.commit()
    
    return