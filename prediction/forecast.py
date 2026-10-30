from pathlib import Path
import pandas as pd

from .api_client import fetch_traffic_data
from .feature_engineering import build_features
from .model_loader import load_trained_model


API_BASE_URL = "http://127.0.0.1:5000"


def fetch_latest_record():
    """Get the latest available traffic record from the API."""

    import requests

    url = f"{API_BASE_URL}/api/mysql/traffic/latest"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    return response.json()


def predict_next_hour():

    # 1. Discover the latest record automatically.
    latest_record = fetch_latest_record()

    latest_timestamp = pd.to_datetime(
        latest_record["recorded_at"]
    )

    print(f"Latest database record: {latest_timestamp}")

    # 2. Fetch seven days of historical data.
    # This provides enough history for the 24-hour features.
    end_date = latest_timestamp.strftime("%Y-%m-%d")
    start_date = (
        latest_timestamp - pd.Timedelta(days=7)
    ).strftime("%Y-%m-%d")

    records = fetch_traffic_data(start_date, end_date)

    # 3. Generate features.
    features_df = build_features(records)

    # 4. Make sure the range endpoint includes the latest record.
    if features_df.empty or features_df.index[-1] != latest_timestamp:
        raise ValueError(
            "The latest record from the API was not found "
            "at the end of the historical data."
        )

    # 5. Load the trained model.
    model, model_features, horizon = load_trained_model()

    # 6. Select the latest feature row.
    latest_features = features_df[model_features].iloc[[-1]]

    # 7. Validate the features.
    if latest_features.isna().any().any():
        missing = latest_features.columns[
            latest_features.isna().any()
        ].tolist()

        raise ValueError(
            f"Cannot predict because these features are missing: {missing}. "
            "Fetch a wider historical range or investigate missing hours."
        )

    # 8. Generate the prediction.
    prediction = model.predict(latest_features)[0]

    # 9. Calculate the forecast timestamp.
    forecast_timestamp = (
        latest_timestamp + pd.Timedelta(hours=horizon)
    )

    return {
        "last_recorded_at": latest_timestamp,
        "forecast_for": forecast_timestamp,
        "last_traffic_volume": int(
            latest_features["traffic_volume"].iloc[0]
        ),
        "predicted_traffic_volume": round(float(prediction), 2)
    }

def save_prediction(result):
    """Save predictions without duplicate forecast timestamps."""

    project_root = Path(__file__).resolve().parent.parent
    results_folder = project_root / "results"

    results_folder.mkdir(parents=True, exist_ok=True)

    csv_path = results_folder / "predictions.csv"

    new_prediction = pd.DataFrame([{
        "last_recorded_at": result["last_recorded_at"],
        "forecast_for": result["forecast_for"],
        "last_traffic_volume": result["last_traffic_volume"],
        "predicted_traffic_volume": result["predicted_traffic_volume"]
    }])

    if csv_path.exists():
        existing_predictions = pd.read_csv(csv_path)

        # Remove any previous prediction for this forecast timestamp.
        existing_predictions["forecast_for"] = pd.to_datetime(
            existing_predictions["forecast_for"]
        )

        existing_predictions = existing_predictions[
            existing_predictions["forecast_for"]
            != pd.Timestamp(result["forecast_for"])
        ]
        
        if existing_predictions.empty:
            predictions = new_prediction
        else:
            predictions = pd.concat(
                [existing_predictions, new_prediction],
                ignore_index=True
        )
    else:
        predictions = new_prediction

    predictions.to_csv(csv_path, index=False)

    print(f"\nPrediction saved to: {csv_path}")

if __name__ == "__main__":

    result = predict_next_hour()

    print("\n========== TRAFFIC FORECAST ==========")
    print(f"Last recorded time: {result['last_recorded_at']}")
    print(f"Last traffic volume: {result['last_traffic_volume']}")
    print(f"Forecast time: {result['forecast_for']}")
    print(
        f"Predicted traffic volume: "
        f"{result['predicted_traffic_volume']}"
    )
    print("======================================")

    save_prediction(result)