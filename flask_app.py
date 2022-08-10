from flask import Flask, redirect, render_template, request, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy, inspect
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

def object_as_dict(obj):                                                                                                                                           
    return {c.key: getattr(obj, c.key)                                                                                                                             
        for c in inspect(obj).mapper.column_attrs}

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
            return f"The api throwed the following error: {response.status_code}"

    except requests.exceptions.HTTPError as e:
            return f"The code encountered the following HTTPError error: {e}"
    except requests.exceptions.RequestException as e:
        return f"The code encountered the following RequestException error: {e}"
    except Exception as e:
        return f"The code encountered the following error: {e}"

    for curr,currencyName in result.get("symbols", {}).items():
        currObj = CurrenySymbols(curr=curr,currName=currencyName)
        db.session.add(currObj)
    
    db.session.commit()

    endDateTimeObj = datetime.today()
    startDateTimeObj = datetime.today() - timedelta(days=30)

    end_date = endDateTimeObj.strftime("%Y-%m-%d")
    start_date = startDateTimeObj.strftime("%Y-%m-%d")
    base = "USD"

    url = url = f"https://api.apilayer.com/exchangerates_data/timeseries?start_date={start_date}&end_date={end_date}&base={base}"

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
            return f"The api throwed the following error: {response.status_code}"

    except requests.exceptions.HTTPError as e:
            return f"The code encountered the following HTTPError error: {e}"
    except requests.exceptions.RequestException as e:
        return f"The code encountered the following RequestException error: {e}"
    except Exception as e:
        return f"The code encountered the following error: {e}"

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
    
    return "Successfully initialized the databases!"

@app.route('/', methods=['GET'])
def root():
    return render_template('index.html') # Return index.html 

@app.route('/getAllExchangeRates')
def getAllExchangeRates():

    try: 
        dataObj = db.session().query(ExchangeRateRow).order_by(ExchangeRateRow.date.desc()).first()
    except Exception as e:
        return {"Error": f"The code encountered the following error {e}"}
    rates = object_as_dict(dataObj)

    response = {
        "base_code": "USD",
        "rates": rates
    }

    return response

# @app.route('/getPastExchangeRates')
# def getPastExchangeRates():
#     if request.method == 'GET':
#         request_data = request.args.to_dict()
#     else:
#         request_data = request.get_json()

#     startDate = request_data.get("start_date", None)
#     endDate = request_data.get("start_date", None)
#     currency = request_data.get("currency", None)

#     if startDate == None or endDate == None or currency == None:
#         return {"Error": "Please provide all there parameters start_date, end_date and currency"}

#     try: 
#         dataObj = db.session().query(ExchangeRateRow).filter_by(ExchangeRateRow.date.desc()).first()
#     except Exception as e:
#         return f"The code encountered the following error {e}"
#     rates = object_as_dict(dataObj)

#     response = {
#         "base_code": "USD",
#         "rates": rates
#     }

    return response


if __name__ == "__main__":
  app.run()