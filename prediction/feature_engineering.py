import pandas as pd


# These names and their order must match the trained model.
MODEL_FEATURES = [
    "hour",
    "day_of_week",
    "month",
    "is_weekend",
    "traffic_volume",
    "lag_1h",
    "lag_3h",
    "lag_24h",
    "rolling_7h",
    "rolling_24h"
]


def build_features(records):
    """
    Convert API traffic records into the features required
    by the trained Random Forest model.
    """

    if not records:
        raise ValueError("No traffic records were received from the API.")

    # Convert API records into a Pandas DataFrame.
    df = pd.DataFrame(records)

    # Convert timestamps and traffic volume to the correct data types.
    df["recorded_at"] = pd.to_datetime(df["recorded_at"])
    df["traffic_volume"] = pd.to_numeric(
        df["traffic_volume"],
        errors="coerce"
    )

    # Use timestamps as the DataFrame index.
    df = df.set_index("recorded_at")

    # Sort records from oldest to newest.
    df = df.sort_index()

    # Avoid calculating features from duplicate timestamps.
    if df.index.has_duplicates:
        raise ValueError("Duplicate timestamps found in traffic records.")

    # Create a complete hourly timeline.
    # Missing hours will contain NaN values.
    df = df.asfreq("h")

    # Extract calendar features.
    df["hour"] = df.index.hour
    df["day_of_week"] = df.index.dayofweek
    df["month"] = df.index.month
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # Calculate lag features.
    df["lag_1h"] = df["traffic_volume"].shift(1)
    df["lag_3h"] = df["traffic_volume"].shift(3)
    df["lag_24h"] = df["traffic_volume"].shift(24)

    # Calculate rolling averages using previous hours only.
    previous_traffic = df["traffic_volume"].shift(1)

    df["rolling_7h"] = previous_traffic.rolling(
        window=7,
        min_periods=7
    ).mean()

    df["rolling_24h"] = previous_traffic.rolling(
        window=24,
        min_periods=24
    ).mean()

    # Return only the features required by the model,
    # keeping them in the correct order.
    return df[MODEL_FEATURES]