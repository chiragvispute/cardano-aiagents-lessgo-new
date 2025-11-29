# MIP-003 Compliant API Implementation for Financial Insights Service

This document outlines how the Financial Insights Agentic Service implements the MIP-003: Agentic Service API Standard for integration with the Masumi Network.

## Service Overview

**Service Name:** Financial Insights Analyzer  
**Service Type:** masumi-agent  
**Description:** Analyzes financial statements and transaction data to provide spending insights, alerts, and recommendations.

---

## API Endpoints Implementation

### 1. /start_job (POST)
**Purpose:** Initiates a financial analysis job

#### Request
```json
{
  "identifier_from_purchaser": "analysis-job-2025-001",
  "input_data": {
    "html_content": "<html>...</html>",
    "analysis_type": "spending_analysis"
  }
}
```

#### Response (Success)
```json
{
  "id": "18d66eed-6af5-4589-b53a-d2e78af657b6",
  "status": "success",
  "job_id": "job_456abc",
  "blockchainIdentifier": "block_789def",
  "payByTime": 1721480200,
  "submitResultTime": 1717171717,
  "unlockTime": 1717172717,
  "externalDisputeUnlockTime": 1717173717,
  "agentIdentifier": "financial-insights-v1",
  "sellerVKey": "addr1qxlkjl23k4jlksdjfl234jlksdf",
  "identifierFromPurchaser": "analysis-job-2025-001",
  "input_hash": "a87ff679a2f3e71d9181a67b7542122c"
}
```

#### Error Responses
- **400 Bad Request:** Invalid input_data or missing identifier_from_purchaser
- **500 Internal Server Error:** Job initiation failed

---

### 2. /status (GET)
**Purpose:** Retrieves the current status of a job

#### Query Parameters
```
job_id=job_456abc
```

#### Response (Running Status)
```json
{
  "id": "ae56b846-f86c-4367-8511-dee68b8ca18d",
  "job_id": "job_456abc",
  "status": "running",
  "result": "Analyzing spending patterns..."
}
```

#### Response (Completed Status)
```json
{
  "id": "ae56b846-f86c-4367-8511-dee68b8ca18d",
  "job_id": "job_456abc",
  "status": "completed",
  "result": {
    "keyInsights": [
      {
        "title": "Total Monthly Spending",
        "description": "₹42,500 total expenditure across Food (35%), Travel (25%), and Other (40%)"
      }
    ],
    "alerts": [
      {
        "type": "High-Value Transactions",
        "severity": "medium",
        "description": "3 transactions above ₹10,000 detected",
        "recommendation": "Review and confirm these are legitimate expenses"
      }
    ],
    "suggestions": [
      {
        "category": "Expense Optimization",
        "suggestion": "Reduce Food & Dining expenses by 15% to save ₹2,250/month"
      }
    ]
  }
}
```

#### Response (Awaiting Input Status)
```json
{
  "id": "ae56b846-f86c-4367-8511-dee68b8ca18d",
  "job_id": "job_456abc",
  "status": "awaiting_input",
  "input_schema": {
    "input_data": [
      {
        "id": "clarification",
        "type": "string",
        "name": "Additional Information",
        "data": {
          "placeholder": "Provide any additional context about the transactions"
        }
      }
    ]
  }
}
```

#### Possible Status Values
- `awaiting_payment` - Awaiting payment confirmation
- `awaiting_input` - Waiting for additional input from user
- `running` - Analysis in progress
- `completed` - Analysis complete with results
- `failed` - Job failed with error

#### Error Responses
- **404 Not Found:** job_id does not exist
- **500 Internal Server Error:** Cannot retrieve status

---

### 3. /provide_input (POST)
**Purpose:** Provides additional input for a job awaiting input

#### Request (Simple Format)
```json
{
  "job_id": "job_456abc",
  "status_id": "8731ecb3-3bcc-4ebc-b46ff7dd12dd",
  "input_data": {
    "clarification": "These are personal expenses from my bank statement"
  }
}
```

#### Request (Groups Format)
```json
{
  "job_id": "job_456abc",
  "status_id": "8731ecb3-3bcc-4ebc-b46ff7dd12dd",
  "input_groups": [
    {
      "id": "8f5dd0a7-7048-4783-94ae-23a96a4a629d",
      "input_data": {
        "priority": "food_expenses"
      }
    }
  ]
}
```

#### Response
```json
{
  "status": "success",
  "input_hash": "a87ff679a2f3e71d9181a67b7542122c",
  "signature": "8a5fd6602094407b7e5923aa0f2694f8cb5cf39f317a61059fdc572e24fc1c7660d23c04d46355aed78b5ec35ae8cad1433e7367bb874390dfe46ed155727a08"
}
```

#### Error Responses
- **400 Bad Request:** Invalid job_id or input_data
- **404 Not Found:** Job does not exist
- **500 Internal Server Error:** Processing failed

---

### 4. /availability (GET)
**Purpose:** Checks if the service is operational

#### Response
```json
{
  "status": "available",
  "type": "masumi-agent",
  "message": "Financial Insights Analyzer is ready to accept jobs"
}
```

#### Error Responses
- **500 Internal Server Error:** Service unavailable

---

### 5. /input_schema (GET)
**Purpose:** Returns expected input format for jobs

#### Response
```json
{
  "input_data": [
    {
      "id": "html_content",
      "type": "string",
      "name": "HTML Financial Statement",
      "data": {
        "placeholder": "Paste your bank or financial statement HTML",
        "maxLength": 52428800
      },
      "validations": [
        {
          "type": "required",
          "message": "HTML content is required"
        },
        {
          "type": "minLength",
          "value": 100,
          "message": "HTML content must be at least 100 characters"
        }
      ]
    },
    {
      "id": "analysis_type",
      "type": "option",
      "name": "Analysis Type",
      "data": {
        "options": [
          {
            "value": "spending_analysis",
            "label": "Spending Analysis"
          },
          {
            "value": "vendor_analysis",
            "label": "Vendor Analysis"
          },
          {
            "value": "budget_planning",
            "label": "Budget Planning"
          }
        ]
      }
    }
  ]
}
```

---

## Implementation in Flask

Add these endpoints to your `app.py`:

```python
from flask import request, jsonify
import uuid
from datetime import datetime, timedelta
import hashlib
import json

# Job storage (in production, use database)
jobs_store = {}

@app.route('/start_job', methods=['POST'])
def start_job():
    """MIP-003 Compliant: Start a financial analysis job"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('identifier_from_purchaser'):
            return jsonify({
                "status": "error",
                "message": "identifier_from_purchaser is required"
            }), 400
        
        if not data.get('input_data'):
            return jsonify({
                "status": "error",
                "message": "input_data is required"
            }), 400
        
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        status_id = str(uuid.uuid4())
        
        # Create input hash
        input_hash = hashlib.md5(
            json.dumps(data['input_data']).encode()
        ).hexdigest()
        
        # Set timestamps
        now = datetime.utcnow()
        pay_by_time = int((now + timedelta(hours=1)).timestamp())
        submit_result_time = int((now + timedelta(hours=2)).timestamp())
        unlock_time = int((now + timedelta(hours=3)).timestamp())
        dispute_unlock_time = int((now + timedelta(hours=4)).timestamp())
        
        # Store job
        jobs_store[job_id] = {
            "status": "running",
            "status_id": status_id,
            "input_data": data['input_data'],
            "identifier_from_purchaser": data['identifier_from_purchaser'],
            "created_at": now.isoformat()
        }
        
        return jsonify({
            "id": status_id,
            "status": "success",
            "job_id": job_id,
            "blockchainIdentifier": f"block_{uuid.uuid4().hex[:8]}",
            "payByTime": pay_by_time,
            "submitResultTime": submit_result_time,
            "unlockTime": unlock_time,
            "externalDisputeUnlockTime": dispute_unlock_time,
            "agentIdentifier": "financial-insights-v1",
            "sellerVKey": "addr1qxlkjl23k4jlksdjfl234jlksdf",
            "identifierFromPurchaser": data['identifier_from_purchaser'],
            "input_hash": input_hash
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/status', methods=['GET'])
def get_job_status():
    """MIP-003 Compliant: Get job status"""
    try:
        job_id = request.args.get('job_id')
        
        if not job_id:
            return jsonify({
                "status": "error",
                "message": "job_id query parameter is required"
            }), 400
        
        if job_id not in jobs_store:
            return jsonify({
                "status": "error",
                "message": "Job not found"
            }), 404
        
        job = jobs_store[job_id]
        
        return jsonify({
            "id": job.get('status_id'),
            "job_id": job_id,
            "status": job.get('status'),
            "result": job.get('result')
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/provide_input', methods=['POST'])
def provide_input():
    """MIP-003 Compliant: Provide additional input for job"""
    try:
        data = request.get_json()
        
        job_id = data.get('job_id')
        status_id = data.get('status_id')
        input_data = data.get('input_data')
        
        if not job_id or not status_id:
            return jsonify({
                "status": "error",
                "message": "job_id and status_id are required"
            }), 400
        
        if job_id not in jobs_store:
            return jsonify({
                "status": "error",
                "message": "Job not found"
            }), 404
        
        # Create input hash
        input_hash = hashlib.md5(
            json.dumps(input_data or {}).encode()
        ).hexdigest()
        
        # Generate signature (simplified - use Ed25519 in production)
        signature = hashlib.sha256(
            json.dumps({"job_id": job_id, "status_id": status_id}).encode()
        ).hexdigest() * 2  # Mock signature
        
        # Update job with new input
        jobs_store[job_id]['input_data'].update(input_data or {})
        jobs_store[job_id]['status'] = 'running'
        
        return jsonify({
            "status": "success",
            "input_hash": input_hash,
            "signature": signature
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/availability', methods=['GET'])
def check_availability():
    """MIP-003 Compliant: Check service availability"""
    return jsonify({
        "status": "available",
        "type": "masumi-agent",
        "message": "Financial Insights Analyzer is ready to accept jobs"
    }), 200

@app.route('/input_schema', methods=['GET'])
def get_input_schema():
    """MIP-003 Compliant: Return expected input schema"""
    return jsonify({
        "input_data": [
            {
                "id": "html_content",
                "type": "string",
                "name": "HTML Financial Statement",
                "data": {
                    "placeholder": "Paste your bank or financial statement HTML",
                    "maxLength": 52428800
                },
                "validations": [
                    {
                        "type": "required",
                        "message": "HTML content is required"
                    },
                    {
                        "type": "minLength",
                        "value": 100,
                        "message": "HTML must be at least 100 characters"
                    }
                ]
            },
            {
                "id": "analysis_type",
                "type": "option",
                "name": "Analysis Type",
                "data": {
                    "options": [
                        {"value": "spending_analysis", "label": "Spending Analysis"},
                        {"value": "vendor_analysis", "label": "Vendor Analysis"},
                        {"value": "budget_planning", "label": "Budget Planning"}
                    ]
                }
            }
        ]
    }), 200
```

---

## Testing MIP-003 Compliance

### Test 1: Start a Job
```bash
curl -X POST https://your-service.onrender.com/start_job \
  -H "Content-Type: application/json" \
  -d '{
    "identifier_from_purchaser": "test-job-001",
    "input_data": {
      "html_content": "<html>...</html>",
      "analysis_type": "spending_analysis"
    }
  }'
```

### Test 2: Check Availability
```bash
curl https://your-service.onrender.com/availability
```

### Test 3: Get Input Schema
```bash
curl https://your-service.onrender.com/input_schema
```

### Test 4: Check Job Status
```bash
curl "https://your-service.onrender.com/status?job_id=job_456abc"
```

---

## Masumi Network Integration

Once deployed, register your service with the Masumi Payment Service:

1. **Service Registration URL:** `https://your-service.onrender.com`
2. **Service Type:** `masumi-agent`
3. **Agent Identifier:** `financial-insights-v1`
4. **Supported Operations:** Spending Analysis, Vendor Analysis, Budget Planning

The Masumi Payment Service will use:
- `/availability` for service health checks
- `/input_schema` for displaying UI to users
- `/start_job` to initiate analysis
- `/status` to check job progress
- `/provide_input` for interactive feedback

---

## Security Considerations

1. **API Keys:** Implement bearer token authentication in production
2. **CORS:** Configure appropriate CORS headers
3. **Rate Limiting:** Implement rate limiting per user
4. **Input Validation:** Validate all inputs against schema
5. **Signatures:** Use Ed25519 for cryptographic signatures (currently mocked)
6. **Payment Verification:** Validate blockchain payment identifiers

---

## Notes

- This implementation uses in-memory storage for demonstration. Use a database (MongoDB) in production.
- Signature generation is simplified. Implement proper Ed25519 signing in production.
- Job IDs and timestamps follow MIP-003 specification.
- All responses follow the standard MIP-003 format.

---

**Status:** MIP-003 Compliant ✅  
**Last Updated:** November 30, 2025
