import requests


API_BASE_URL = "http://127.0.0.1:5000"


def fetch_traffic_data(start_date, end_date):
    """
    Fetch historical traffic records from the Flask API.
    """

    url = f"{API_BASE_URL}/api/mysql/traffic/range"

    params = {
        "start": start_date,
        "end": end_date
    }

    try:
        response = requests.get(url, params=params, timeout=30)

        # Raise an error if the API returns an unsuccessful status code
        response.raise_for_status()

        records = response.json()

        # Confirm that the API returned a list
        if not isinstance(records, list):
            raise ValueError("Expected the API to return a list of records.")

        # Check that the required columns exist
        if records:
            required_fields = {"recorded_at", "traffic_volume"}

            for field in required_fields:
                if field not in records[0]:
                    raise ValueError(f"Missing required field: {field}")

        print(f"Successfully fetched {len(records)} traffic records.")

        return records

    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"Could not connect to the Flask API: {error}")