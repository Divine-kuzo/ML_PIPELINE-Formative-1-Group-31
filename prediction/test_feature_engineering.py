from .api_client import fetch_traffic_data
from .feature_engineering import build_features, MODEL_FEATURES


# Fetch historical records.
records = fetch_traffic_data(
    start_date="2018-09-28",
    end_date="2018-09-30"
)

# Generate model features.
features = build_features(records)

print("\nGenerated features:")
print(features.tail())

print("\nFeature columns:")
print(features.columns.tolist())

print("\nNumber of feature columns:")
print(len(features.columns))

print("\nMissing values in the latest row:")
print(features.iloc[-1].isna().sum())

print("\nLatest feature row:")
print(features.iloc[-1])