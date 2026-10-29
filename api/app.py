from flask import Flask, jsonify
from config import mongo_client, mysql_engine
from mongodb_routes import mongodb_bp
from mysql_routes import mysql_bp

app = Flask(__name__)

app.register_blueprint(mysql_bp)
app.register_blueprint(mongodb_bp)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Traffic Data API",
        "endpoints": {
            "mysql": "/api/mysql/traffic",
            "mongodb": "/api/mongodb/traffic",
        },
    })


@app.route("/health", methods=["GET"])
def health():
    status = {
        "mysql": "connected",
        "mongodb": "connected",
    }

    try:
        with mysql_engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
    except Exception:
        status["mysql"] = "disconnected"

    try:
        mongo_client.admin.command("ping")
    except Exception:
        status["mongodb"] = "disconnected"

    http_status = 200 if all(
        value == "connected" for value in status.values()
    ) else 503

    return jsonify(status), http_status


if __name__ == "__main__":
    app.run(debug=True)