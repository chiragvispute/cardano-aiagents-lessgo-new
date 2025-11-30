from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import base64
import hashlib
from datetime import datetime, timedelta
import dotenv
import os
import json
import threading
import tempfile

# Import the insights agent
from insights_agent import analyze_html_file

dotenv.load_dotenv()

app = Flask(__name__)

# FULL CORS FIX for Sokosumi
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Masumi agent ID from your .env
AGENT_IDENTIFIER = os.getenv("AGENT_IDENTIFIER", "financial-insights-v1")
SELLER_VKEY = os.getenv("SELLER_VKEY", "addr1qxlkjl23k4jlksdjfl234jlksdf")

app.url_map.strict_slashes = False

# In-memory job store
jobs = {}


def get_job(job_id):
    return jobs.get(job_id)


def save_job(job_id, data):
    """Save job to in-memory store"""
    jobs[job_id] = data


def process_job_async(job_id, html_content):
    """Process HTML analysis in background thread"""
    def _process():
        try:
            print(f"[PROCESSING] Starting analysis for job: {job_id}")
            
            # Save HTML to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_html_path = f.name
            
            try:
                # Analyze HTML file with Gemini
                analysis_result = analyze_html_file(temp_html_path)
                
                if analysis_result is None:
                    raise ValueError("Failed to analyze HTML file")
                
                # Convert CrewOutput to string
                result_str = str(analysis_result).strip()
                
                # Extract JSON from the result
                json_start = result_str.find('{')
                json_end = result_str.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = result_str[json_start:json_end]
                    analysis_data = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
                
                # Update job with results
                job = get_job(job_id)
                job['status'] = 'completed'
                job['result'] = analysis_data
                job['completed_at'] = datetime.utcnow().isoformat()
                
                save_job(job_id, job)
                print(f"[SUCCESS] Job completed: {job_id}")
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_html_path):
                    os.remove(temp_html_path)
        
        except Exception as e:
            print(f"[ERROR] Job processing failed: {job_id} - {str(e)}")
            job = get_job(job_id)
            job['status'] = 'failed'
            job['error'] = str(e)
            job['completed_at'] = datetime.utcnow().isoformat()
            save_job(job_id, job)
    
    # Start processing in background thread
    thread = threading.Thread(target=_process, daemon=True)
    thread.start()


# ============================================
# MIP-003 ENDPOINTS
# ============================================

@app.get("/availability")
def availability():
    """Check service availability"""
    return jsonify({
        "status": "available",
        "type": "masumi-agent",
        "message": "Financial Insights Agent is live"
    }), 200


@app.get("/input_schema")
def input_schema():
    """Return expected input schema"""
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
                "validations": [
                    {"type": "required"}
                ]
            }
        ]
    }), 200


@app.post("/start_job")
def start_job():
    """Start a new financial analysis job"""
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

        # Decode base64 HTML
        try:
            html_content = base64.b64decode(input_data["html_file"]).decode("utf-8")
        except Exception as e:
            return jsonify({"status": "error", "message": f"Invalid base64 file: {str(e)}"}), 400

        if not html_content or len(html_content) < 10:
            return jsonify({"status": "error", "message": "HTML content is empty"}), 400

        # Generate IDs
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        status_id = str(uuid.uuid4())
        blockchain_id = f"block_{uuid.uuid4().hex[:8]}"

        # Create input hash
        input_hash = hashlib.md5(html_content.encode()).hexdigest()

        # Set timestamps (Unix timestamps)
        now = datetime.utcnow()
        pay_by_time = int((now + timedelta(hours=1)).timestamp())
        submit_result_time = int((now + timedelta(hours=2)).timestamp())
        unlock_time = int((now + timedelta(hours=3)).timestamp())
        dispute_unlock_time = int((now + timedelta(hours=4)).timestamp())

        # Create job record
        job_data = {
            "job_id": job_id,
            "status": "processing",
            "status_id": status_id,
            "html_content": html_content,
            "identifier_from_purchaser": identifier,
            "created_at": now.isoformat(),
            "result": None,
            "error": None
        }

        # Save job
        save_job(job_id, job_data)

        # Start async processing with Gemini
        process_job_async(job_id, html_content)

        print(f"[MIP-003] Job started: {job_id}")

        return jsonify({
            "id": status_id,
            "status": "success",
            "job_id": job_id,
            "blockchainIdentifier": blockchain_id,
            "payByTime": pay_by_time,
            "submitResultTime": submit_result_time,
            "unlockTime": unlock_time,
            "externalDisputeUnlockTime": dispute_unlock_time,
            "agentIdentifier": AGENT_IDENTIFIER,
            "sellerVKey": SELLER_VKEY,
            "identifierFromPurchaser": identifier,
            "input_hash": input_hash
        }), 200

    except Exception as e:
        print(f"[ERROR] /start_job: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.get("/status")
def status():
    """Get job status and results"""
    job_id = request.args.get("job_id")

    if not job_id:
        return jsonify({"status": "error", "message": "job_id query parameter required"}), 400

    job = get_job(job_id)
    if not job:
        return jsonify({"status": "error", "message": "Job not found"}), 404

    response = {
        "id": job.get("status_id"),
        "job_id": job_id,
        "status": job["status"]
    }

    # Include result if job is completed
    if job.get("result"):
        response["result"] = job["result"]

    # Include error if job failed
    if job.get("error"):
        response["error"] = job["error"]

    # Include completion timestamp
    if job.get("completed_at"):
        response["completed_at"] = job["completed_at"]

    return jsonify(response), 200


@app.post("/provide_input")
def provide_input():
    """Handle additional input for jobs (optional)"""
    data = request.get_json()
    job_id = data.get("job_id")

    if not job_id:
        return jsonify({"status": "error", "message": "job_id required"}), 400

    job = get_job(job_id)
    if not job:
        return jsonify({"status": "error", "message": "Job not found"}), 404

    return jsonify({"status": "success", "message": "Input received"}), 200


# ============================================
# HEALTH CHECK
# ============================================

@app.get("/")
def root():
    """Root endpoint"""
    return jsonify({
        "message": "Masumi MIP-003 Agent Online",
        "service": "Financial Insights Analyzer",
        "status": "ready"
    }), 200


@app.get("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Financial Insights Analyzer",
        "version": "1.0.0"
    }), 200


# ============================================
# ENTRYPOINT
# ============================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

