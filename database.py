from sqlalchemy import create_engine
import requests

base = "USD"
API_KEY = "P2dnLPUw5Pz0HyGerxzFhaJLb89sASMq"
url = f"https://api.apilayer.com/exchangerates_data/latest?base={base}"

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
        print("The api throwed the following error:", response.status_code)

except requests.exceptions.HTTPError as e:
        print("The code encountered the following HTTPError error:", e)
except requests.exceptions.RequestException as e:
    print("The code encountered the following RequestException error:", e)
except Exception as e:
    print("The code encountered the following error:", e)

usd = result.get("rates", {}).get("USD", 0)
cad = result.get("rates", {}).get("CAD", 0)
inr = result.get("rates", {}).get("INR", 0)
eur = result.get("rates", {}).get("EUR", 0)
aed = result.get("rates", {}).get("AED", 0)
bhd = result.get("rates", {}).get("BHD", 0)
hkd = result.get("rates", {}).get("HKD", 0)
jpy = result.get("rates", {}).get("JPY", 0)
strDate = result.get("date", "")
date = strDate.replace("-", "")

try:
    engine = create_engine("mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username="BDATProject",
        password="myExchangeRates",
        hostname="BDATProject.mysql.pythonanywhere-services.com",
        databasename="BDATProject$ExchangeRates",
    ))
    
    with engine.connect() as connection:
        query="INSERT INTO  `BDATProject$ExchangeRates`.`exchangeRates` (`date` ,`USD` ,`CAD` ,`INR`, `EUR`, `AED`,`BHD`,`HKD`,`JPY`) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        data=(date, usd, cad, inr, eur, aed, bhd, hkd, jpy)
            
        id=connection.execute(query,data)

except Exception as e:
    print("The code encountered the following error",e)