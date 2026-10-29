from datetime import date, datetime


def parse_datetime(value):
    """Convert a date/time string into a Python datetime."""
    if not value:
        raise ValueError("recorded_at is required.")

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        ).replace(tzinfo=None)
    except (ValueError, AttributeError):
        raise ValueError(
            "Use a valid date/time, e.g. 2025-01-01T08:00:00."
        )


def parse_date(value):
    """Convert a YYYY-MM-DD string into a date."""
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValueError("Use the date format YYYY-MM-DD.")


def parse_record_payload(data):
    """Validate the main fields used when creating a record."""
    if not isinstance(data, dict):
        raise ValueError("The request body must be a JSON object.")

    recorded_at = parse_datetime(data.get("recorded_at"))

    traffic_volume = data.get("traffic_volume")
    if traffic_volume is None:
        raise ValueError("traffic_volume is required.")

    try:
        traffic_volume = int(traffic_volume)
    except (ValueError, TypeError):
        raise ValueError("traffic_volume must be a whole number.")

    if traffic_volume < 0:
        raise ValueError("traffic_volume cannot be negative.")

    observed = data.get("observed", True)
    if not isinstance(observed, bool):
        raise ValueError("observed must be true or false.")

    calendar = data.get("calendar") or {}
    weather = data.get("weather") or {}

    if not isinstance(calendar, dict) or not isinstance(weather, dict):
        raise ValueError("calendar and weather must be JSON objects.")

    holiday = calendar.get("holiday") or {}
    if not isinstance(holiday, dict):
        raise ValueError("calendar.holiday must be a JSON object.")

    return {
        "recorded_at": recorded_at,
        "event_date": recorded_at.date(),
        "traffic_volume": traffic_volume,
        "observed": observed,
        "calendar": calendar,
        "holiday": holiday,
        "weather": weather,
    }


def record_to_json(row):
    """Convert a database record into a JSON-friendly dictionary."""
    if row is None:
        return None

    result = dict(row)

    for key, value in result.items():
        if isinstance(value, (datetime, date)):
            result[key] = value.isoformat()

    return result


def mongo_to_json(document):
    """Convert a MongoDB document into a JSON-friendly dictionary."""
    if document is None:
        return None

    document["_id"] = str(document["_id"])
    document["recorded_at"] = document["recorded_at"].isoformat()
    return document