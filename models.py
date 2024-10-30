from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(int, primary_key=True, index=True)
    destination = Column(String, index=True)
    start_date = Column(Date)
    end_date = Column(Date)
    activities = Column(int)