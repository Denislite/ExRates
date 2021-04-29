import requests
from datetime import datetime
from xml.etree import ElementTree
from fastapi import FastAPI
from models import model
from database.base import SessionLocal, engine


URL_ECB_DAILY = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
URL_ECB_90DAYS = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml'
URL_ECB_ALL = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.xml'

model.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def update_rates(our_url):
    req = requests.get(our_url)
    envelope = ElementTree.fromstring(req.content)

    namespaces = {
        "gesmes": "http://www.gesmes.org/xml/2002-08-01",
        "eurofxref": "http://www.ecb.int/vocabulary/2002-08-01/eurofxref",
    }

    data = envelope.findall(".//eurofxref:Cube/eurofxref:Cube[@time]", namespaces)
    for d in data:
        time = datetime.strptime(d.attrib["time"], "%Y-%m-%d").date()
        print(time)
        rates = { c.attrib["currency"]: (c.attrib["rate"]) for c in list(d) }
        print(rates)


if __name__ == "__main__":
    update_rates(URL_ECB_ALL)