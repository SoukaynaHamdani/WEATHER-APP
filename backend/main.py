import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import date
import requests
import pandas as pd  # For export

from models import Base, Location, Weather

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("Set DATABASE_URL in your .env file")

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
app = FastAPI()

def create_tables():
    Base.metadata.create_all(bind=engine)
create_tables()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemas (what requests/responses look like)
class LocationCreate(BaseModel):
    name: str
    latitude: float
    longitude: float

class LocationOut(LocationCreate):
    id: int
    class Config:
        orm_mode = True

class WeatherCreate(BaseModel):
    location_id: int
    date: date
    description: str
    temperature: float

class WeatherOut(WeatherCreate):
    id: int
    class Config:
        orm_mode = True

# Welcome message
@app.get("/")
def read_root():
    return {
        "message": "Weather app backend started!",
        "creator": "YOUR NAME HERE",
        "info": "Built for PM Accelerator - see our LinkedIn: Product Manager Accelerator"
    }

# CRUD for Location
@app.post("/locations", response_model=LocationOut, status_code=status.HTTP_201_CREATED)
def create_location(loc: LocationCreate, db: Session = Depends(get_db)):
    location = Location(name=loc.name, latitude=loc.latitude, longitude=loc.longitude)
    db.add(location)
    db.commit()
    db.refresh(location)
    return location

@app.get("/locations", response_model=list[LocationOut])
def get_locations(db: Session = Depends(get_db)):
    return db.query(Location).all()

@app.get("/locations/{id}", response_model=LocationOut)
def get_location(id: int, db: Session = Depends(get_db)):
    loc = db.query(Location).filter(Location.id == id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return loc

@app.put("/locations/{id}", response_model=LocationOut)
def update_location(id: int, loc: LocationCreate, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    location.name = loc.name
    location.latitude = loc.latitude
    location.longitude = loc.longitude
    db.commit()
    db.refresh(location)
    return location

@app.delete("/locations/{id}")
def delete_location(id: int, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.id == id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    db.delete(location)
    db.commit()
    return {"detail": "Location deleted"}

# CRUD for Weather
@app.post("/weather", response_model=WeatherOut)
def add_weather(weather: WeatherCreate, db: Session = Depends(get_db)):
    weather_rec = Weather(**weather.dict())
    db.add(weather_rec)
    db.commit()
    db.refresh(weather_rec)
    return weather_rec

@app.get("/weather", response_model=list[WeatherOut])
def get_weather(location_id: int = None, db: Session = Depends(get_db)):
    if location_id:
        return db.query(Weather).filter(Weather.location_id == location_id).all()
    return db.query(Weather).all()

@app.put("/weather/{id}", response_model=WeatherOut)
def update_weather(id: int, weather: WeatherCreate, db: Session = Depends(get_db)):
    weather_rec = db.query(Weather).filter(Weather.id == id).first()
    if not weather_rec:
        raise HTTPException(status_code=404, detail="Weather record not found")
    for field, value in weather.dict().items():
        setattr(weather_rec, field, value)
    db.commit()
    db.refresh(weather_rec)
    return weather_rec

@app.delete("/weather/{id}")
def delete_weather(id: int, db: Session = Depends(get_db)):
    weather_rec = db.query(Weather).filter(Weather.id == id).first()
    if not weather_rec:
        raise HTTPException(status_code=404, detail="Weather record not found")
    db.delete(weather_rec)
    db.commit()
    return {"detail": "Weather record deleted"}

# Weather API integration example (OpenWeatherMap)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
@app.get("/external/weather")
def get_external_weather(city: str):
    # Replace this endpoint with OpenWeatherMap or any free weather API
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    resp = requests.get(url)
    if not resp.ok:
        raise HTTPException(status_code=404, detail="City not found or API error")
    data = resp.json()
    return {
        "city": city,
        "description": data["weather"][0]["description"],
        "temperature": data["main"]["temp"]
    }

# Example for data export (CSV, JSON)
@app.get("/export/weather")
def export_weather(format: str = "csv", db: Session = Depends(get_db)):
    query = db.query(Weather).all()
    records = [w.__dict__ for w in query]
    for record in records:
        record.pop("_sa_instance_state", None)
    df = pd.DataFrame(records)
    if format == "csv":
        return df.to_csv(index=False)
    elif format == "json":
        return df.to_json(orient="records")
    else:
        raise HTTPException(status_code=400, detail="Format not supported")

# Error handling built-in -- all endpoints gracefully report "not found" or wrong data!

