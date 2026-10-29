# Traffic Volume Forecasting — Group 31

## Project Overview

This project develops an end-to-end machine learning pipeline to predict hourly traffic volume using the Metro Interstate Traffic Volume dataset.

## Task 1: Time-Series Analysis and Modeling

- Cleaned and processed hourly traffic records.
- Conducted exploratory data analysis using five analytical questions and visualizations.
- Created lagged features and moving averages.
- Trained and compared three Random Forest experiments.
- Selected the model with historical features based on evaluation results.

## Model Results

| Experiment                          |     MAE |    RMSE |    R² |
| ----------------------------------- | ------: | ------: | ----: |
| Baseline Random Forest              | 154.202 | 232.765 | 0.986 |
| Random Forest + Historical Features | 143.821 | 221.735 | 0.987 |
| Tuned Random Forest                 | 143.921 | 221.878 | 0.987 |

## Project Components

- Task 1: EDA and model training
- Task 2: SQL and MongoDB databases
- Task 3: API development
- Task 4: End-to-end forecasting integration

## Dataset

`data/traffic_hourly_cleaned.csv`

## Model

`models/traffic_forecasting_model.joblib`

## Notebook

`notebooks/Traffic_Volume_Time_Series_EDA_and_Model.ipynb`

## Running the Project

Open the notebook in Google Colab or Jupyter and install the dependencies listed in `requirements.txt`.

The dataset is available in the repository for database integration.

# Task 2: Database Implementation & Analytical Queries(SQL and MongoDB databases)

This tasks sets up, populates, and queries both the relational (**MySQL**) and (**MongoDB**) databases using the cleaned dataset (`data/processed/traffic_hourly_cleaned.csv`).

---

## 1. Prerequisites & Environment Setup
In the project root, define the required database credentials in the environment configuration file.

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_DATABASE=interstate_traffic_db

# MongoDB Configuration
MONGO_URI=mongodb://127.0.0.1:27017/
MONGO_DB_NAME=interstate_traffic_db

### Install required python dependencies

pip install pymysql sqlalchemy pymongo pandas python-dotenv

### Initialize schema

mysql -u root -p < database/mysql/schema.sql

### Load data

python database/mysql/load_data_mysql.py

### Execute Queries

mysql -u root -p interstate_traffic_db < database/mysql/queries.sql

### MongoDB

### Ingest Data

Ensure the local MongoDB daemon is running on port 27017, then execute:

python database/mongodb/load_data_mongo.py

### Execute queries

mongosh interstate_traffic_db database/mongodb/queries.js

## Task 3: Traffic Data API

A Flask API was developed to perform CRUD operations on traffic data stored in MySQL and MongoDB.

### MySQL Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/mysql/traffic` | Retrieve traffic records |
| POST | `/api/mysql/traffic` | Create a traffic record |
| GET | `/api/mysql/traffic/<record_id>` | Retrieve one record |
| PUT | `/api/mysql/traffic/<record_id>` | Update a record |
| DELETE | `/api/mysql/traffic/<record_id>` | Delete a record |
| GET | `/api/mysql/traffic/latest` | Retrieve the latest record |
| GET | `/api/mysql/traffic/range?start=YYYY-MM-DD&end=YYYY-MM-DD` | Retrieve records within a date range |

### MongoDB Endpoints

The same operations are available through `/api/mongodb/traffic`, including retrieving a record by ID, retrieving the latest record, and filtering records by date range.

### Running the API

From the project root, activate the virtual environment and run:

```bash
python api/app.py
```

The API runs locally at `http://127.0.0.1:5000`.

### Testing

All CRUD operations, latest-record endpoints, and date-range endpoints were tested successfully for both MySQL and MongoDB. Successful requests returned the expected HTTP status codes.
