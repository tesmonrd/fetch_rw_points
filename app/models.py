from sqlalchemy import Column, Integer, String
from .database import Base


class Transaction(Base):
    __tablename__ = "Transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    payer = Column(String(255), index=True)
    points = Column(Integer)
    timestamp = Column(String(255))