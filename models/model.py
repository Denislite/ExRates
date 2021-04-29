from sqlalchemy import Column, String, Date
from database.base import Base


class Curr(Base):
    __tablename__ = "currency"
    ticker = Column(String)
    date = Column(Date)
    rates = Column(String, primary_key=True)
