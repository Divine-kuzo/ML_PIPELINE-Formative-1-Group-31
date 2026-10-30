import pandas as pd

from .api_client import fetch_traffic_data
from .feature_engineering import build_features
from .model_loader import load_trained_model


def predict_next_hour(start_date, end_date):

    # 1. Fetch historical traffic data.
    records = fetch_traffic_data(start_date, end_date)

    # 2. Generate features.
    features_df = build_features(records)

    # 3. Load the trained model.
    model, model_features, horizon = load_trained_model()

    # 4. Select the latest available feature row.
    latest_features = features_df[model_features].iloc[[-1]]

    # 5. Check for missing values.
    if latest_features.isna().any().any():
        raise ValueError(
            "Cannot predict: the latest feature row contains missing values."
        )

    # 6. Generate prediction.
    prediction = model.predict(latest_features)[0]

    # 7. Determine the forecast timestamp.
    latest_timestamp = features_df.index[-1]
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


if __name__ == "__main__":

    result = predict_next_hour(
        start_date="2018-09-28",
        end_date="2018-09-30"
    )

    print("\n========== TRAFFIC FORECAST ==========")
    print(f"Last recorded time: {result['last_recorded_at']}")
    print(f"Last traffic volume: {result['last_traffic_volume']}")
    print(f"Forecast time: {result['forecast_for']}")
    print(
        f"Predicted traffic volume: "
        f"{result['predicted_traffic_volume']}"
    )
    print("======================================")