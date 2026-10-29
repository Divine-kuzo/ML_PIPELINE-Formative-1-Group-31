import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


# Load .env from the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# MySQL settings
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "interstate_traffic_db")

mysql_url = URL.create(
    "mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

mysql_engine = create_engine(
    mysql_url,
    pool_pre_ping=True,
)

# MongoDB settings
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://127.0.0.1:27017/"
)
MONGO_DB_NAME = os.getenv(
    "MONGO_DB_NAME",
    "interstate_traffic_db"
)

mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
mongo_db = mongo_client[MONGO_DB_NAME]
mongo_collection = mongo_db["traffic_records"]