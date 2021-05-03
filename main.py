import sqlite3
import json
import requests
from datetime import datetime
from xml.etree import ElementTree
from fastapi import FastAPI, HTTPException
from models import model
from database.base import SessionLocal, engine
from typing import Optional
import ast
from os import path


URL_ECB_DAILY = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
URL_ECB_90DAYS = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml'
URL_ECB_ALL = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml'
DATABASE_URL = 'sql_app.db'

model.Base.metadata.create_all(bind=engine)

app = FastAPI()

dbase = sqlite3.connect("sql_app.db")

cursor = dbase.cursor()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def update_rates(our_url, pref):
    if pref == "init":
        req = requests.get(our_url)
        envelope = ElementTree.fromstring(req.content)

        namespaces = {
            "gesmes": "http://www.gesmes.org/xml/2002-08-01",
            "eurofxref": "http://www.ecb.int/vocabulary/2002-08-01/eurofxref",
        }

        data = envelope.findall(".//eurofxref:Cube/eurofxref:Cube[@time]", namespaces)
        for d in data:
            date = datetime.strptime(d.attrib["time"], "%Y-%m-%d").date()
            rates = { c.attrib["currency"]: (c.attrib["rate"]) for c in list(d) }
            rates["EUR"] = "1"
            rates = json.dumps(rates)
            cursor.execute("""
            INSERT INTO currency(date, rates)
            VALUES(?, ?)
            ON CONFLICT(date)
            DO NOTHING""",((date), (rates)))
            dbase.commit()


@app.on_event("startup")
async def initial_update():
    await update_rates(URL_ECB_ALL,"init")


@app.on_event("shutdown")
async def end_update():
    return 1


@app.get("/historical")
async def historical(base: Optional[str] = None, start_at: Optional[str] = None,
                     end_at: Optional[str] = None, date: Optional[str] = None):

    if not base:
        base = "EUR"

    if date:
        #print('okey')
        currency = cursor.execute(f"""
        SELECT date, rates
        FROM currency
        WHERE date = ? """, (date,))

    if start_at and not end_at:
        #print('okey1')
        currency = cursor.execute(f"""
        SELECT date, rates
        FROM currency
        WHERE date > ? """, (start_at,))

    if end_at and not start_at:
        #print('okey2')
        currency = cursor.execute(f"""
        SELECT date, rates
        FROM currency
        WHERE date < ? """, (end_at,))

    if start_at and end_at:
        #print('okey3')
        currency = cursor.execute(f"""
        SELECT date, rates
        FROM currency
        WHERE date BETWEEN ? AND ? """, (start_at, end_at,))

    currency = cursor.fetchall()
    result = {}
    for i, j in enumerate(currency):
        result_temp = {}
        date_value = currency[i][0]
        rates_temp = ast.literal_eval(currency[i][1])
        #print(rates_temp)
        #print(date_value)
        base_value = float(rates_temp.get(base))
        for key, value in rates_temp.items():
            result_temp[key] = float(value) / base_value
        result[date_value] = result_temp

    return {"rates":result,"base":base}


@app.get("/latest")
async def latest(base: Optional[str] = None):

    if not base:
        base = "EUR"

    currency = cursor.execute(f"""
    SELECT date, rates
    FROM currency
    ORDER BY date DESC LIMIT 1;""")

    currency = cursor.fetchall()
    rates_temp = ast.literal_eval(currency[0][1])
    #форматирование значения курса сделать
    base_value = float(rates_temp.get(base))

    result = {}
    for key, value in rates_temp.items():
        result[key] = float(value)/base_value

    if result == {}:
        raise HTTPException(status_code=404, detail="Invalid currency or invalid date")
    else:
        return {currency[0][0]: result, "base": base}


@app.get("/")
async def home():
    return "welcome to my app"
