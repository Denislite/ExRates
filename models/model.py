from sqlalchemy import Column, Date, JSON
from database.base import Base


class Curr(Base):
    __tablename__ = "currency"
    date = Column(Date, primary_key=True)
    rates = Column(JSON)
