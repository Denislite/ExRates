![1](https://user-images.githubusercontent.com/71836579/122655540-b2fbaf00-d15b-11eb-858a-6f81d56f079a.png)
# ExRates
Service for current and historical foreign exchange rates
# Installation
```
git clone https://github.com/Denislite/ExRates
cd ExRates
virtualenv env
source env/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
# Usage
Get the latest foreign exchange rates.
```http
    GET /latest 
```
Get historical rates for any day since 1999.
```http
    GET /historical?date=2010-01-12
```
Choose your rate base. Default base is EUR.
```http
    GET /latest?base=USD
```
Get historical rates for a time period.
```http
    GET /historical?start_at=2018-01-01&end_at=2018-09-01
```
Get the historical rates against a different rate base.
```http
    GET /historical?start_at=2018-01-01&end_at=2018-09-01&base=USD
```
# Stack
ExRates is based on FastAPI framework. SQLite is used as a database.
#### Libraries used:
- Requests
- JSON
- The ElementTree XML API
- SQLAlchemy
