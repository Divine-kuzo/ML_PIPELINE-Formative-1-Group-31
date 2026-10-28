import os
from pathlib import Path
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
MONGO_DB = os.getenv("MONGO_DB_NAME", "interstate_traffic_db")
COLLECTION_NAME = "traffic_records"

print(f"Connecting to MongoDB at {MONGO_URI}...")
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[COLLECTION_NAME]

# Drop existing collection to ensure idempotency
collection.drop()

data_path = BASE_DIR / "data" / "processed" / "traffic_hourly_cleaned.csv"
print(f"Loading cleaned data from: {data_path} ...")
df = pd.read_csv(data_path)

df["recorded_at"] = pd.to_datetime(df["date_time"])
df["event_date"] = df["recorded_at"].dt.strftime("%Y-%m-%d")
df["day_name"] = df["recorded_at"].dt.day_name()
df["hour"] = df["recorded_at"].dt.hour
df["is_weekend"] = df["recorded_at"].dt.dayofweek.isin([5, 6])
df["holiday_name"] = df["holiday"].fillna("None")
df["is_holiday"] = df["holiday_name"] != "None"

print("Transforming rows to embedded documents...")
documents = []
for row in df.itertuples(index=False):
    doc = {
        "recorded_at": row.recorded_at.to_pydatetime(),
        "traffic_volume": int(row.traffic_volume) if pd.notna(row.traffic_volume) else None,
        "observed": bool(row.observed),
        "calendar": {
            "date": row.event_date,
            "hour": int(row.hour),
            "day_name": row.day_name,
            "is_weekend": bool(row.is_weekend),
            "holiday": {
                "is_holiday": bool(row.is_holiday),
                "name": str(row.holiday_name)
            }
        },
        "weather": {
            "temp_kelvin": float(row.temp) if pd.notna(row.temp) else None,
            "rain_1h_mm": float(row.rain_1h) if pd.notna(row.rain_1h) else None,
            "snow_1h_mm": float(row.snow_1h) if pd.notna(row.snow_1h) else 0.0,
            "clouds_coverage_pct": int(row.clouds_all),
            "main": str(row.weather_main),
            "description": str(row.weather_description)
        }
    }
    documents.append(doc)

print("Inserting documents into MongoDB in chunks...")
batch_size = 5000
for i in range(0, len(documents), batch_size):
    collection.insert_many(documents[i:i + batch_size])

# Create useful indexes for time-series filtering
collection.create_index([("recorded_at", ASCENDING)], unique=True)
collection.create_index([("calendar.date", ASCENDING)])
collection.create_index([("calendar.day_name", ASCENDING)])
collection.create_index([("weather.main", ASCENDING)])

print(f"MongoDB Ingestion completed! Total documents: {collection.count_documents({})}")