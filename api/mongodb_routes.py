from datetime import datetime, time, timedelta
from bson import ObjectId
from flask import Blueprint, jsonify, request
from pymongo.errors import DuplicateKeyError

from config import mongo_collection
from utils import (
    mongo_to_json,
    parse_date,
    parse_record_payload,
)

mongodb_bp = Blueprint(
    "mongodb_api", __name__, url_prefix="/api/mongodb"
)


def find_record(record_id):
    if not ObjectId.is_valid(record_id):
        return None

    return mongo_collection.find_one({"_id": ObjectId(record_id)})


@mongodb_bp.route("/traffic", methods=["GET", "POST"])
def traffic_records():
    if request.method == "GET":
        try:
            limit = int(request.args.get("limit", 100))
            if not 1 <= limit <= 1000:
                raise ValueError
        except ValueError:
            return jsonify({
                "error": "limit must be between 1 and 1000."
            }), 400

        records = mongo_collection.find().sort(
            "recorded_at", -1
        ).limit(limit)

        return jsonify([mongo_to_json(record) for record in records])

    try:
        data = parse_record_payload(request.get_json(silent=True))
        calendar = data["calendar"]
        holiday = data["holiday"]
        weather = data["weather"]
        recorded_at = data["recorded_at"]

        document = {
            "recorded_at": recorded_at,
            "traffic_volume": data["traffic_volume"],
            "observed": data["observed"],
            "calendar": {
                "date": recorded_at.date().isoformat(),
                "hour": recorded_at.hour,
                "day_name": calendar.get(
                    "day_name", recorded_at.strftime("%A")
                ),
                "is_weekend": calendar.get("is_weekend", False),
                "holiday": {
                    "is_holiday": holiday.get("is_holiday", False),
                    "name": holiday.get("name"),
                },
            },
            "weather": {
                "temp_kelvin": weather.get("temp_kelvin"),
                "rain_1h_mm": weather.get("rain_1h_mm", 0),
                "snow_1h_mm": weather.get("snow_1h_mm", 0),
                "clouds_coverage_pct": weather.get(
                    "clouds_coverage_pct", 0
                ),
                "main": weather.get("main"),
                "description": weather.get("description"),
            },
        }

        result = mongo_collection.insert_one(document)
        saved_record = mongo_collection.find_one(
            {"_id": result.inserted_id}
        )

        return jsonify({
            "message": "Traffic record created.",
            "record": mongo_to_json(saved_record),
        }), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except DuplicateKeyError:
        return jsonify({
            "error": "A record with this date/time may already exist."
        }), 409


@mongodb_bp.route("/traffic/latest", methods=["GET"])
def latest_traffic_record():
    record = mongo_collection.find_one(
        sort=[("recorded_at", -1)]
    )

    if not record:
        return jsonify({"error": "No traffic records found."}), 404

    return jsonify(mongo_to_json(record))


@mongodb_bp.route("/traffic/range", methods=["GET"])
def traffic_by_date_range():
    try:
        start_date = parse_date(request.args.get("start"))
        end_date = parse_date(request.args.get("end"))

        if start_date > end_date:
            raise ValueError("start must be on or before end.")

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    start_time = datetime.combine(start_date, time.min)
    end_time = datetime.combine(
        end_date + timedelta(days=1), time.min
    )

    records = mongo_collection.find({
        "recorded_at": {
            "$gte": start_time,
            "$lt": end_time,
        }
    }).sort("recorded_at", 1)

    return jsonify([mongo_to_json(record) for record in records])


@mongodb_bp.route(
    "/traffic/<record_id>", methods=["GET", "PUT", "DELETE"]
)
def traffic_record_detail(record_id):
    if not ObjectId.is_valid(record_id):
        return jsonify({"error": "Invalid record ID."}), 400

    object_id = ObjectId(record_id)

    if request.method == "GET":
        record = find_record(record_id)

        if not record:
            return jsonify({"error": "Traffic record not found."}), 404

        return jsonify(mongo_to_json(record))

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

        result = mongo_collection.update_one(
            {"_id": object_id},
            {"$set": updates},
        )

        if result.matched_count == 0:
            return jsonify({"error": "Traffic record not found."}), 404

        return jsonify({
            "message": "Traffic record updated.",
            "record": mongo_to_json(find_record(record_id)),
        })

    result = mongo_collection.delete_one({"_id": object_id})

    if result.deleted_count == 0:
        return jsonify({"error": "Traffic record not found."}), 404

    return jsonify({"message": "Traffic record deleted."})