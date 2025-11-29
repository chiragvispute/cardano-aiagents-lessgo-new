from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import base64
import hashlib
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Allow / and /input_schema/ etc.
app.url_map.strict_slashes = False

# In-memory job store
jobs = {}


def save_job(job_id, data):
    jobs[job_id] = data


def get_job(job_id):
    return jobs.get(job_id)


# ----------------------------------------------------------
# 🔥 MIP-003 REQUIRED ENDPOINT
# ----------------------------------------------------------
@app.get("/availability")
def availability():
    return {
        "status": "available",
        "type": "masumi-agent",
        "message": "Financial Insights Agent is live"
    }, 200


# ----------------------------------------------------------
# 🔥 MIP-003 REQUIRED ENDPOINT
# Sokosumi uses this to build the UI form
# ----------------------------------------------------------
@app.get("/input_schema")
def input_schema():
    return {
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
                "validations": [
                    {"type": "required"}
                ]
            }
        ]
    }, 200


# ----------------------------------------------------------
# 🔥 MIP-003 REQUIRED ENDPOINT
# Accepts base64 encoded HTML file
# ----------------------------------------------------------
@app.post("/start_job")
def start_job():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "Invalid JSON"}), 400

        identifier_from_purchaser = data.get("identifier_from_purchaser")
        input_data = data.get("input_data", {})

        if not identifier_from_purchaser:
            return jsonify({"status": "error", "message": "identifier_from_purchaser is required"}), 400

        if "html_file" not in input_data:
            return jsonify({"status": "error", "message": "html_file (base64) is required"}), 400

        # ---- Decode HTML base64 ----
        try:
            html_content = base64.b64decode(input_data["html_file"]).decode("utf-8")
        except Exception:
            return jsonify({"status": "error", "message": "Invalid base64 HTML file"}), 400

        # ---- Generate IDs ----
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        status_id = str(uuid.uuid4())
        blockchain_id = f"block_{uuid.uuid4().hex[:8]}"

        # Create input hash
        input_hash = hashlib.md5(html_content.encode()).hexdigest()

        now = datetime.utcnow()
        pay_by_time = int((now + timedelta(hours=1)).timestamp())
        submit_result_time = int((now + timedelta(hours=2)).timestamp())
        unlock_time = int((now + timedelta(hours=3)).timestamp())
        dispute_unlock_time = int((now + timedelta(hours=4)).timestamp())

        # ---- Store job ----
        jobs[job_id] = {
            "job_id": job_id,
            "status": "awaiting_payment",
            "status_id": status_id,
            "html_content": html_content,
            "identifier_from_purchaser": identifier_from_purchaser,
            "created_at": now.isoformat(),
            "result": None
        }

        print(f"[MIP-003] Job created: {job_id}")

        # ---- Respond according to MIP-003 ----
        return jsonify({
            "id": status_id,
            "status": "success",
            "job_id": job_id,
            "blockchainIdentifier": blockchain_id,
            "payByTime": pay_by_time,
            "submitResultTime": submit_result_time,
            "unlockTime": unlock_time,
            "externalDisputeUnlockTime": dispute_unlock_time,
            "agentIdentifier": "financial-insights-v1",     # YOUR AGENT ID
            "sellerVKey": "addr1qxlkjl23k4jlksdjfl234jlksdf",
            "identifierFromPurchaser": identifier_from_purchaser,
            "input_hash": input_hash
        }), 200

    except Exception as e:
        print("[ERROR] /start_job:", e)
        return jsonify({"status": "error", "message": str(e)}), 500


# ----------------------------------------------------------
# 🔥 MIP-003 REQUIRED ENDPOINT
# Called by Sokosumi to refresh job status
# ----------------------------------------------------------
@app.get("/status")
def status():
    job_id = request.args.get("job_id")

    if not job_id:
        return jsonify({"status": "error", "message": "job_id required"}), 400

    job = get_job(job_id)
    if not job:
        return jsonify({"status": "error", "message": "Job not found"}), 404

    response = {
        "id": str(uuid.uuid4()),
        "job_id": job_id,
        "status": job["status"]
    }

    if job["status"] == "completed":
        response["result"] = job["result"]

    return jsonify(response), 200


# ----------------------------------------------------------
# Fake endpoint for payment callback (you can integrate later)
# In production: Masumi Payment Service will notify you.
# ----------------------------------------------------------
@app.post("/simulate_payment")
def simulate_payment():
    data = request.get_json()
    job_id = data.get("job_id")

    if job_id not in jobs:
        return jsonify({"status": "error", "message": "Job not found"}), 404

    jobs[job_id]["status"] = "completed"
    jobs[job_id]["result"] = "Payment received. HTML parsed successfully."

    return jsonify({"status": "success"}), 200


# ----------------------------------------------------------
# Root route (optional)
# ----------------------------------------------------------
@app.get("/")
def home():
    return "Masumi MIP-003 Compatible Financial Agent Running", 200


# ----------------------------------------------------------
# LOCAL DEV ENTRYPOINT
# ----------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
