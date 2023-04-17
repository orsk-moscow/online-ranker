from sqlalchemy import Column, Float, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Venue(Base):
    """A SQLAlchemy model representing a venue with its attributes."""

    __tablename__ = "info"  # The name of the table in the database

    venue_id = Column(
        Integer, primary_key=True, index=True
    )  # The unique identifier of the venue, used as the primary key
    conversions_per_impression = Column(Float)  # The ratio of conversions to impressions
    price_range = Column(Integer)  # The price range of the venue
    rating = Column(Float)  # The average rating of the venue
    popularity = Column(Float)  # The popularity of the venue
    retention_rate = Column(Float)  # The rate of retention for the venue's customers
