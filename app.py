from flask import Flask, jsonify, request
from insights_agent import analyze_spending_patterns
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/insights', methods=['GET'])
def get_insights():
    """
    Get financial insights from transaction data
    Returns: JSON with keyInsights, alerts, and suggestions
    """
    try:
        print("🚀 Generating financial insights...")
        
        # Run the insights agent
        analysis_result = analyze_spending_patterns()
        
        if analysis_result is None:
            return jsonify({
                "success": False,
                "error": "No analysis result",
                "message": "Failed to generate insights"
            }), 500
        
        # Convert CrewOutput to string
        result_str = str(analysis_result).strip()
        
        # Extract JSON from the result
        # Look for JSON object in the result
        try:
            # Find the start of JSON (first '{')
            json_start = result_str.find('{')
            json_end = result_str.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = result_str[json_start:json_end]
                analysis_data = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
            
            # Validate structure
            if "keyInsights" not in analysis_data or "alerts" not in analysis_data or "suggestions" not in analysis_data:
                raise ValueError("Missing required fields: keyInsights, alerts, suggestions")
            
            return jsonify({
                "success": True,
                "keyInsights": analysis_data.get("keyInsights", []),
                "alerts": analysis_data.get("alerts", []),
                "suggestions": analysis_data.get("suggestions", [])
            }), 200
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {str(e)}")
            print(f"Raw result: {result_str[:500]}")
            return jsonify({
                "success": False,
                "error": f"Invalid JSON response from AI: {str(e)}",
                "message": "Failed to parse insights"
            }), 500
        
    except Exception as e:
        print(f"❌ Error generating insights: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Failed to generate insights"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Cardano Insights API",
        "version": "1.0.0"
    }), 200

@app.route('/', methods=['GET'])
def index():
    """API documentation"""
    return jsonify({
        "name": "Cardano Insights API",
        "version": "1.0.0",
        "endpoints": {
            "GET /health": "Health check",
            "GET /insights": "Get financial insights from transaction data"
        },
        "documentation": "Use Postman to access /insights endpoint"
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('INSIGHTS_API_PORT', 5002))
    app.run(debug=True, host='0.0.0.0', port=port)
