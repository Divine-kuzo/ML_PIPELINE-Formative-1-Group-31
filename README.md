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
