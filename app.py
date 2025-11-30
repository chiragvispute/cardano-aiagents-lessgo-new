from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import base64
import hashlib
from datetime import datetime, timedelta
import dotenv
import os

dotenv.load_dotenv()

app = Flask(__name__)

# FULL CORS FIX for Sokosumi
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Masumi agent ID from your .env
AGENT_IDENTIFIER = os.getenv("AGENT_IDENTIFIER")

app.url_map.strict_slashes = False

jobs = {}

def get_job(job_id):
    return jobs.get(job_id)


@app.get("/availability")
def availability():
    return jsonify({
        "status": "available",
        "type": "masumi-agent",
        "message": "Financial Insights Agent is live"
    }), 200


@app.get("/input_schema")
def input_schema():
    return jsonify({
        "input_data": [
            {
                "id": "html_file",
                "type": "file",
                "name": "Google Pay Activity File (.html)",
                "data": {
                    "accept": ".html",
                    "maxSize": 5000000,
                    "outputFormat": "base64"
                },
                "validations": [{"type": "required"}]
            }
        ]
    }), 200


@app.post("/start_job")
def start_job():
    try:
        if not request.is_json:
            return jsonify({"status": "error", "message": "Content-Type must be application/json"}), 415

        data = request.get_json()
        identifier = data.get("identifier_from_purchaser")
        input_data = data.get("input_data", {})

        if not identifier:
            return jsonify({"status": "error", "message": "identifier_from_purchaser required"}), 400

        if "html_file" not in input_data:
            return jsonify({"status": "error", "message": "html_file base64 required"}), 400

        # decode
        try:
            html = base64.b64decode(input_data["html_file"]).decode("utf-8")
        except:
            return jsonify({"status": "error", "message": "Invalid base64 file"}), 400

        job_id = f"job_{uuid.uuid4().hex[:8]}"
        status_id = str(uuid.uuid4())
        blockchain_id = f"block_{uuid.uuid4().hex[:8]}"

        now = datetime.utcnow()

        jobs[job_id] = {
            "job_id": job_id,
            "status": "awaiting_payment",
            "status_id": status_id,
            "html_content": html,
            "identifier": identifier
        }

        return jsonify({
            "id": status_id,
            "status": "success",
            "job_id": job_id,
            "blockchainIdentifier": blockchain_id,
            "payByTime": int((now + timedelta(hours=1)).timestamp()),
            "submitResultTime": int((now + timedelta(hours=2)).timestamp()),
            "unlockTime": int((now + timedelta(hours=3)).timestamp()),
            "externalDisputeUnlockTime": int((now + timedelta(hours=4)).timestamp()),
            "agentIdentifier": AGENT_IDENTIFIER,
            "sellerVKey": os.getenv("SELLER_VKEY"),
            "identifierFromPurchaser": identifier,
            "input_hash": hashlib.md5(html.encode()).hexdigest()
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.get("/status")
def status():
    job_id = request.args.get("job_id")

    job = get_job(job_id)
    if not job:
        return jsonify({"status": "error", "message": "job not found"}), 404

    return jsonify({
        "id": str(uuid.uuid4()),
        "job_id": job_id,
        "status": job["status"],
        "result": job.get("result")
    }), 200


@app.get("/")
def root():
    return jsonify({"message": "Masumi MIP-003 agent online"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
