from urllib import response
from flask import Flask, redirect, render_template, request, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy, inspect
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["DEBUG"] = True

# MySQL configurations
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

# External API key to https://apilayer.com/marketplace/exchangerates_data-api
API_KEY = "P2dnLPUw5Pz0HyGerxzFhaJLb89sASMq"

# Databaseschema / Class for exchangerates
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

# Convert sqlalchemy object to json dictionary so that flask can return it to webpage
def object_as_dict(obj):                                                                                                                                           
    return {c.key: getattr(obj, c.key)                                                                                                                             
        for c in inspect(obj).mapper.column_attrs}

# Index page call / Dashboard page
@app.route('/', methods=['GET'])
def root():
    return render_template('index.html') # Return index.html 

# This method will overwrite the databases if they exist and initialize them
# Should only be used when starting the application
# When starting the application it will not have historical data for graphs so using this method
# to populate some historical data
@app.route("/initialize", methods=["GET"])
def initialize():

    # Drop and re create all the tables
    db.drop_all()
    db.create_all()

    # Fetch data for the past 30 days
    endDateTimeObj = datetime.today()
    startDateTimeObj = datetime.today() - timedelta(days=30)

    end_date = endDateTimeObj.strftime("%Y-%m-%d")
    start_date = startDateTimeObj.strftime("%Y-%m-%d")
    base = "USD"

    url = f"https://api.apilayer.com/exchangerates_data/timeseries?start_date={start_date}&end_date={end_date}&base={base}"

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

# Get the latest exchange rates for all the currencies
@app.route('/getAllExchangeRates')
def getAllExchangeRates():

    try:
        # Query the exchangerates table, sort it in descending order by date and get the last row for latest values
        dataObj = db.session().query(ExchangeRateRow).order_by(ExchangeRateRow.date.desc()).first()
    except Exception as e:
        return {"Error": f"The code encountered the following error {e}"}
    
    # Convert the response into dictionary / json
    rates = object_as_dict(dataObj)
    # Remove date from the currencies
    date = rates.get("date", None)
    rates.pop("date", None)

    response = {
        "base_code": "USD",
        "date": date,
        "rates": rates
    }

    return response

# Get past exchanges rates based on the start_time and end_time provided by the user
# If the user provides a curreny show data for that currency else show data for all the currencies
@app.route('/getPastExchangeRates')
def getPastExchangeRates():
    if request.method == 'GET':
        request_data = request.args.to_dict()
    else:
        request_data = request.get_json()

    startDate = request_data.get("start_date", None)
    endDate = request_data.get("end_date", None)
    currency = request_data.get("currency", None)

    if startDate == None or endDate == None:
        return {"Error": "Please provide the parameters start_date, end_date"}

    try: 
        startDateStr = startDate.replace("-", "")
        endDateStr = endDate.replace("-", "")
        dataObj = db.session().query(ExchangeRateRow).filter(ExchangeRateRow.date.between(startDateStr, endDateStr)).all()
    except Exception as e:
        return f"The code encountered the following error {e}"
    response = {
        "base": "USD",
        "rates": {}
    }
    for obj in dataObj:
        rates = object_as_dict(obj)
        exchangeRates = {}
        for cur, value in rates.items():
            if cur == "date":
                continue
            # If no currency is provided fetch data for all the currencies else only for specified currency
            if currency is None:
                exchangeRates[cur] = value
            if currency is not None and cur == currency:
                exchangeRates[cur] = value

        response.get("rates")[rates.get("date", "00000000")] = exchangeRates

    return response


# Get all historical data for a particular currency
@app.route('/getCurrencyExchangeRate')
def getCurrencyExchangeRate():
    if request.method == 'GET':
        request_data = request.args.to_dict()
    else:
        request_data = request.get_json()

    currency = request_data.get("currency", None)

    if currency == None:
        return {"Error": "Please provide the currency"}

    try: 
        dataObj = db.session().query(ExchangeRateRow).all()
    except Exception as e:
        return f"The code encountered the following error {e}"
    response = {
        "base": "USD",
        "rates": {}
    }
    for obj in dataObj:
        rates = object_as_dict(obj)
        exchangeRates = {}
        for cur, value in rates.items():
            if cur == "date":
                continue
            if currency is not None and cur == currency:
                exchangeRates[cur] = value

        response.get("rates")[rates.get("date", "00000000")] = exchangeRates

    return response


if __name__ == "__main__":
  app.run()