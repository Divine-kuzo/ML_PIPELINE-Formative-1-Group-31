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


## Task 4: Integrated Traffic Prediction Pipeline

### 1. Overview

Task 4 implements an integrated prediction pipeline that connects the Flask API, retrieves historical traffic records from MySQL, performs feature engineering, loads the trained Random Forest model, and predicts traffic volume for the next hour.

The pipeline also saves prediction results in a CSV file for future analysis.

### 2. Pipeline Architecture

The prediction pipeline follows these steps:

1. Fetch the latest available traffic record from the Flask API.
2. Determine the historical date range automatically.
3. Retrieve historical traffic records through the MySQL API endpoint.
4. Preprocess the records and generate time-series features.
5. Load the trained Random Forest model.
6. Generate a next-hour traffic prediction.
7. Save the prediction in `results/predictions.csv`.

### 3. Project Structure

```text
prediction/
    __init__.py
    api_client.py
    feature_engineering.py
    model_loader.py
    forecast.py
    test_api_client.py
    test_feature_engineering.py

models/
    traffic_forecasting_model.joblib

results/
    predictions.csv
```

### 4. Feature Engineering

The pipeline generates the following 10 features required by the trained model:

| Feature | Description |
|---|---|
| hour | Hour of the traffic observation |
| day_of_week | Day of the week |
| month | Month of the observation |
| is_weekend | Indicates whether the day is a weekend |
| traffic_volume | Current traffic volume |
| lag_1h | Traffic volume one hour earlier |
| lag_3h | Traffic volume three hours earlier |
| lag_24h | Traffic volume 24 hours earlier |
| rolling_7h | Average traffic over the previous seven hours |
| rolling_24h | Average traffic over the previous 24 hours |

Missing hourly observations are preserved as missing values rather than being replaced with zero.

### 5. Model Integration

The pipeline loads the saved model from:

`models/traffic_forecasting_model.joblib`

The model is a Random Forest Regressor trained to predict traffic volume one hour ahead.

The saved model artifact also contains the required feature names and prediction horizon.

### 6. Running the Prediction Pipeline

Requirements:
- Python 3.12
- Flask API running locally
- MySQL database populated with traffic records
- Project dependencies installed
- Trained model artifact available

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run the prediction pipeline:

```powershell
python -m prediction.forecast
```

The script automatically discovers the latest available traffic record and retrieves seven days of historical data.

### 7. Example Prediction

Example output from the historical dataset:

```text
Latest database record: 2018-09-30 23:00:00
Successfully fetched 192 traffic records.
Trained model loaded successfully.
Model type: RandomForestRegressor
Prediction horizon: 1 hour(s)

========== TRAFFIC FORECAST ==========
Last recorded time: 2018-09-30 23:00:00
Last traffic volume: 954
Forecast time: 2018-10-01 00:00:00
Predicted traffic volume: 572.3
======================================
```

### 8. Saving Prediction Results

Predictions are stored in:

`results/predictions.csv`

The CSV contains:

- `last_recorded_at`
- `forecast_for`
- `last_traffic_volume`
- `predicted_traffic_volume`

The pipeline prevents duplicate entries for the same forecast timestamp.

### 9. Limitations

The dataset used for this project contains historical traffic observations ending on September 30, 2018.

Therefore, predictions are generated relative to the latest available historical observation. They should not be interpreted as forecasts of current real-world traffic.

The pipeline also requires sufficient consecutive hourly observations to calculate the lag and rolling-average features.
