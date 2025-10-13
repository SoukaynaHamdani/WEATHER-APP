from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from database import Base

class WeatherRecord(Base):
    __tablename__ = "weather_records"
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, index=True)
    location = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    date_queried = Column(DateTime)
    date_from = Column(Date)
    date_to = Column(Date)
    temperature = Column(Float)
    details = Column(String)
    icon_url = Column(String)
    map_url = Column(String)
    youtube_url = Column(String)
 