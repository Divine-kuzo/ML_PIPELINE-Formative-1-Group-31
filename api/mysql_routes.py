from flask import Blueprint, jsonify, request
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from config import mysql_engine
from utils import (
    parse_date,
    parse_record_payload,
    record_to_json,
)

mysql_bp = Blueprint("mysql_api", __name__, url_prefix="/api/mysql")


RECORD_QUERY = """
SELECT
    t.reading_id,
    t.recorded_at,
    t.event_date,
    t.traffic_volume,
    t.observed,
    c.day_name,
    c.is_weekend,
    c.is_holiday,
    c.holiday_name,
    w.temp,
    w.rain_1h,
    w.snow_1h,
    w.clouds_all,
    w.weather_main,
    w.weather_description
FROM traffic_readings AS t
LEFT JOIN calendar_events AS c
    ON t.event_date = c.event_date
LEFT JOIN weather_observations AS w
    ON t.weather_id = w.weather_id
"""


def get_record(record_id):
    query = text(RECORD_QUERY + " WHERE t.reading_id = :record_id")
    with mysql_engine.connect() as connection:
        row = connection.execute(
            query, {"record_id": record_id}
        ).mappings().first()

    return record_to_json(row) if row else None


@mysql_bp.route("/traffic", methods=["GET", "POST"])
def traffic_records():
    if request.method == "GET":
        try:
            limit = int(request.args.get("limit", 100))
            if not 1 <= limit <= 1000:
                raise ValueError
        except ValueError:
            return jsonify({"error": "limit must be between 1 and 1000."}), 400

        query = text(
            RECORD_QUERY
            + " ORDER BY t.recorded_at DESC LIMIT :limit"
        )

        with mysql_engine.connect() as connection:
            rows = connection.execute(
                query, {"limit": limit}
            ).mappings().all()

        return jsonify([record_to_json(row) for row in rows])

    # POST: create a record
    try:
        data = parse_record_payload(request.get_json(silent=True))
        calendar = data["calendar"]
        holiday = data["holiday"]
        weather = data["weather"]

        with mysql_engine.begin() as connection:
            # Add or update the calendar entry for this date.
            connection.execute(
                text("""
                    INSERT INTO calendar_events
                        (event_date, holiday_name, is_holiday,
                         day_name, is_weekend)
                    VALUES
                        (:event_date, :holiday_name, :is_holiday,
                         :day_name, :is_weekend)
                    ON DUPLICATE KEY UPDATE
                        holiday_name = VALUES(holiday_name),
                        is_holiday = VALUES(is_holiday),
                        day_name = VALUES(day_name),
                        is_weekend = VALUES(is_weekend)
                """),
                {
                    "event_date": data["event_date"],
                    "holiday_name": holiday.get("name") or "",
                    "is_holiday": int(holiday.get("is_holiday", False)),
                    "day_name": calendar.get(
                        "day_name", data["recorded_at"].strftime("%A")
                    ),
                    "is_weekend": int(
                        calendar.get("is_weekend", False)
                    ),
                },
            )

            # Add weather for the new observation.
            weather_result = connection.execute(
                text("""
                    INSERT INTO weather_observations
                        (recorded_at, temp, rain_1h, snow_1h,
                         clouds_all, weather_main, weather_description)
                    VALUES
                        (:recorded_at, :temp, :rain_1h, :snow_1h,
                         :clouds_all, :weather_main, :weather_description)
                """),
                {
                    "recorded_at": data["recorded_at"],
                    "temp": weather.get("temp_kelvin"),
                    "rain_1h": weather.get("rain_1h_mm", 0),
                    "snow_1h": weather.get("snow_1h_mm", 0),
                    "clouds_all": weather.get("clouds_coverage_pct", 0),
                    "weather_main": weather.get("main"),
                    "weather_description": weather.get("description"),
                },
            )

            weather_id = weather_result.lastrowid

            result = connection.execute(
                text("""
                    INSERT INTO traffic_readings
                        (recorded_at, event_date, weather_id,
                         traffic_volume, observed)
                    VALUES
                        (:recorded_at, :event_date, :weather_id,
                         :traffic_volume, :observed)
                """),
                {
                    "recorded_at": data["recorded_at"],
                    "event_date": data["event_date"],
                    "weather_id": weather_id,
                    "traffic_volume": data["traffic_volume"],
                    "observed": data["observed"],
                },
            )

            record_id = result.lastrowid

        return jsonify({
            "message": "Traffic record created.",
            "record": get_record(record_id),
        }), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except IntegrityError as error:
        return jsonify({
            "error": str(error.orig)
        }), 409


@mysql_bp.route("/traffic/latest", methods=["GET"])
def latest_traffic_record():
    query = text(
        RECORD_QUERY + " ORDER BY t.recorded_at DESC LIMIT 1"
    )

    with mysql_engine.connect() as connection:
        row = connection.execute(query).mappings().first()

    if not row:
        return jsonify({"error": "No traffic records found."}), 404

    return jsonify(record_to_json(row))


@mysql_bp.route("/traffic/range", methods=["GET"])
def traffic_by_date_range():
    start = request.args.get("start")
    end = request.args.get("end")

    try:
        start_date = parse_date(start)
        end_date = parse_date(end)

        if start_date > end_date:
            raise ValueError("start must be on or before end.")
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    query = text(
        RECORD_QUERY
        + """
        WHERE t.event_date BETWEEN :start_date AND :end_date
        ORDER BY t.recorded_at
        """
    )

    with mysql_engine.connect() as connection:
        rows = connection.execute(
            query,
            {"start_date": start_date, "end_date": end_date},
        ).mappings().all()

    return jsonify([record_to_json(row) for row in rows])


@mysql_bp.route("/traffic/<int:record_id>", methods=["GET", "PUT", "DELETE"])
def traffic_record_detail(record_id):
    if request.method == "GET":
        record = get_record(record_id)

        if not record:
            return jsonify({"error": "Traffic record not found."}), 404

        return jsonify(record)

    if request.method == "PUT":
        data = request.get_json(silent=True)

        if not isinstance(data, dict) or not data:
            return jsonify({"error": "Provide fields to update."}), 400

        updates = {}

        if "traffic_volume" in data:
            try:
                volume = int(data["traffic_volume"])
                if volume < 0:
                    raise ValueError
                updates["traffic_volume"] = volume
            except (ValueError, TypeError):
                return jsonify({
                    "error": "traffic_volume must be a non-negative whole number."
                }), 400

        if "observed" in data:
            if not isinstance(data["observed"], bool):
                return jsonify({
                    "error": "observed must be true or false."
                }), 400
            updates["observed"] = data["observed"]

        if not updates:
            return jsonify({
                "error": "Update traffic_volume and/or observed."
            }), 400

        with mysql_engine.begin() as connection:
            exists = connection.execute(
                text("""
                    SELECT reading_id FROM traffic_readings
                    WHERE reading_id = :record_id
                """),
                {"record_id": record_id},
            ).first()

            if not exists:
                return jsonify({"error": "Traffic record not found."}), 404

            set_clause = ", ".join(
                f"{field} = :{field}" for field in updates
            )
            updates["record_id"] = record_id

            connection.execute(
                text(
                    f"UPDATE traffic_readings SET {set_clause} "
                    "WHERE reading_id = :record_id"
                ),
                updates,
            )

        return jsonify({
            "message": "Traffic record updated.",
            "record": get_record(record_id),
        })

    with mysql_engine.begin() as connection:
        result = connection.execute(
            text("""
                DELETE FROM traffic_readings
                WHERE reading_id = :record_id
            """),
            {"record_id": record_id},
        )

        if result.rowcount == 0:
            return jsonify({"error": "Traffic record not found."}), 404

    return jsonify({"message": "Traffic record deleted."})