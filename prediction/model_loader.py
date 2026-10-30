import joblib
from pathlib import Path


# Locate the model from the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = PROJECT_ROOT / "models" / "traffic_forecasting_model.joblib"


def load_trained_model():
    """
    Load the saved Random Forest model and its metadata.
    """

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found at: {MODEL_PATH}"
        )

    artifact = joblib.load(MODEL_PATH)

    model = artifact["model"]
    features = artifact["features"]
    horizon = artifact["prediction_horizon_hours"]

    print("Trained model loaded successfully.")
    print(f"Model type: {type(model).__name__}")
    print(f"Prediction horizon: {horizon} hour(s)")

    return model, features, horizon