import os
from pathlib import Path
import urllib.parse
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Locate project root and load .env
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

DB_USER = os.getenv("DB_USER", "root").strip()
DB_PASSWORD = os.getenv("DB_PASSWORD", "").strip()
DB_HOST = os.getenv("DB_HOST", "127.0.0.1").strip()
DB_NAME = os.getenv("DB_NAME", "interstate_traffic_db").strip()

try:
  DB_PORT = int(os.getenv("DB_PORT", "3306"))
except (ValueError, TypeError):
  DB_PORT = 3306

# URL-encode user and password safely in case they contain special characters like @, :, !
safe_user = urllib.parse.quote_plus(DB_USER)
safe_password = urllib.parse.quote_plus(DB_PASSWORD)

# If on Ubuntu default socket authentication with empty password, try unix_socket connection
connect_args = {}
if os.path.exists("/var/run/mysqld/mysqld.sock") and (
    not DB_PASSWORD or DB_HOST in ["localhost", "127.0.0.1"]
):
  connect_args["unix_socket"] = "/var/run/mysqld/mysqld.sock"

if safe_password:
  db_url = f"mysql+pymysql://{safe_user}:{safe_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
  db_url = f"mysql+pymysql://{safe_user}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(f"Connecting to database '{DB_NAME}' as user '{DB_USER}'...")
engine = create_engine(db_url, connect_args=connect_args)

# --- Define path to dataset ---
data_path = BASE_DIR / "data" / "processed" / "traffic_hourly_cleaned.csv"

print(f"1. Loading cleaned data from: {data_path} ...")
df = pd.read_csv(data_path)
df["recorded_at"] = pd.to_datetime(df["date_time"])
df["event_date"] = df["recorded_at"].dt.date

# --- 1. Prepare calendar_events ---
print("2. Preparing calendar_events data...")


def get_holiday(series):
  valid = series.dropna()
  return valid.iloc[0] if not valid.empty else "None"


calendar_df = (
    df.groupby("event_date")
    .agg(holiday_name=("holiday", get_holiday))
    .reset_index()
)

calendar_dates = pd.to_datetime(calendar_df["event_date"])
calendar_df["is_holiday"] = calendar_df["holiday_name"] != "None"
calendar_df["day_name"] = calendar_dates.dt.day_name()
calendar_df["is_weekend"] = calendar_dates.dt.dayofweek.isin([5, 6])

# --- 2. Prepare weather_observations ---
print("3. Preparing weather_observations data...")
weather_df = pd.DataFrame({
    "recorded_at": df["recorded_at"],
    "temp": df["temp"].replace({np.nan: None}),
    "rain_1h": df["rain_1h"].replace({np.nan: None}),
    "snow_1h": df["snow_1h"].fillna(0.0),
    "clouds_all": df["clouds_all"].astype(int),
    "weather_main": df["weather_main"],
    "weather_description": df["weather_description"],
})

# --- 3. Insert and map foreign keys ---
with engine.begin() as conn:
  print("4. Inserting calendar_events into MySQL...")
  calendar_df.to_sql(
      "calendar_events", con=conn, if_exists="append", index=False
  )

  print("5. Inserting weather_observations into MySQL...")
  weather_df.to_sql(
      "weather_observations",
      con=conn,
      if_exists="append",
      index=False,
      chunksize=5000,
  )

  print("6. Fetching generated weather_id mapping...")
  weather_lookup = pd.read_sql(
      "SELECT weather_id, recorded_at FROM weather_observations", conn
  )
  weather_lookup["recorded_at"] = pd.to_datetime(weather_lookup["recorded_at"])
  df = df.merge(weather_lookup, on="recorded_at", how="left")

  print("7. Inserting traffic_readings into MySQL...")
  traffic_df = pd.DataFrame({
      "recorded_at": df["recorded_at"],
      "event_date": df["event_date"],
      "weather_id": df["weather_id"],
      "traffic_volume": df["traffic_volume"].replace({np.nan: None}),
      "observed": df["observed"].astype(bool),
  })
  traffic_df.to_sql(
      "traffic_readings",
      con=conn,
      if_exists="append",
      index=False,
      chunksize=5000,
  )

print("Ingestion completed successfully!")