from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import WeatherRecord
from weather_api import geocode_location, get_weather, get_forecast, google_map_url, youtube_search_url
from export_utils import export_as_csv, export_as_json, export_as_md, export_as_pdf
from datetime import datetime, date


Base.metadata.create_all(bind=engine)

app = FastAPI() 
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.post("/weather/")
def create_weather_record(
    query: str, 
    date_from: str, 
    date_to: str, 
    db: Session = Depends(get_db)
):
    try:
        d_from = date.fromisoformat(date_from)
        d_to = date.fromisoformat(date_to)
        assert d_from <= d_to
    except:
        raise HTTPException(status_code=400, detail="Invalid date range")
    geo = geocode_location(query)
    if not geo:
        raise HTTPException(status_code=404, detail="Location not found")
    forecast = get_forecast(geo["latitude"], geo["longitude"], date_from, date_to)
    if not forecast or not forecast.get("temperature_2m_max"):
        raise HTTPException(status_code=404, detail="Forecast not found")
    temperature = max(forecast["temperature_2m_max"])
    record = WeatherRecord(
        query=query,
        location=f"{geo['name']}, {geo['country']}",
        latitude=geo["latitude"],
        longitude=geo["longitude"],
        date_queried=datetime.now(),
        date_from=d_from,
        date_to=d_to,
        temperature=temperature,
        details=f"Max temps: {forecast['temperature_2m_max']}",
        icon_url="",  # You can add icon logic if you want
        map_url=google_map_url(geo['latitude'], geo['longitude'], geo['name']),
        youtube_url=youtube_search_url(geo['name'])
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@app.get("/weather/")
def read_weather_records(db: Session = Depends(get_db)):
    all_rec = db.query(WeatherRecord).all()
    return [ {
        'id': r.id,
        'query': r.query,
        'location': r.location,
        'latitude': r.latitude,
        'longitude': r.longitude,
        'date_from': r.date_from,
        'date_to': r.date_to,
        'date_queried': r.date_queried,
        'temperature': r.temperature,
        'details': r.details,
        'icon_url': r.icon_url,
        'map_url': r.map_url,
        'youtube_url': r.youtube_url
    } for r in all_rec ]

@app.put("/weather/{record_id}")
def update_weather_record(record_id: int, temperature: float = None, details: str = None, db: Session = Depends(get_db)):
    record = db.query(WeatherRecord).filter(WeatherRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    if temperature: record.temperature = temperature
    if details: record.details = details
    db.commit()
    db.refresh(record)
    return record

@app.delete("/weather/{record_id}")
def delete_weather_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(WeatherRecord).filter(WeatherRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return {"message": "Record deleted"}

@app.get("/export/")
def export_weather(format: str = Query("json"), db: Session = Depends(get_db)):
    records = db.query(WeatherRecord).all()
    recs = [
        {'id': r.id, 'query': r.query, 'location': r.location, 'latitude': r.latitude, 'longitude': r.longitude, 'date_from': r.date_from, 'date_to': r.date_to, 'date_queried': r.date_queried, 'temperature': r.temperature, 'details': r.details, 'icon_url': r.icon_url, 'map_url': r.map_url, 'youtube_url': r.youtube_url}
        for r in records
    ]
    if format == "csv":
        return export_as_csv(recs)
    elif format == "json":
        return export_as_json(recs)
    elif format == "md":
        return export_as_md(recs)
    elif format == "pdf":
        return export_as_pdf(recs)
    else:
      raise HTTPException(status_code=400, detail="Format not supported") 