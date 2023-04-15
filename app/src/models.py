from sqlalchemy import Column, Float, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Venue(Base):
    __tablename__ = "info"

    venue_id = Column(Integer, primary_key=True, index=True)
    conversions_per_impression = Column(Float)
    price_range = Column(Integer)
    rating = Column(Float)
    popularity = Column(Float)
    retention_rate = Column(Float)
