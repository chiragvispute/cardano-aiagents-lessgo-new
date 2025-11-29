from flask import Flask, jsonify, request, render_template_string
from insights_agent import analyze_spending_patterns
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# HTML Template for displaying insights
INSIGHTS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Insights Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        .section {
            margin-bottom: 30px;
        }
        .section-title {
            font-size: 1.8em;
            color: white;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 3px solid rgba(255,255,255,0.3);
        }
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }
        .insight-card {
            border-left: 5px solid #667eea;
        }
        .insight-card h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        .insight-card p {
            color: #555;
            line-height: 1.6;
        }
        .alert-card {
            border-left: 5px solid;
        }
        .alert-high {
            border-left-color: #e74c3c;
            background: #fef5f5;
        }
        .alert-medium {
            border-left-color: #f39c12;
            background: #fffaf5;
        }
        .alert-low {
            border-left-color: #27ae60;
            background: #f5fdf7;
        }
        .alert-card .type {
            font-weight: bold;
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        .alert-high .type {
            color: #e74c3c;
        }
        .alert-medium .type {
            color: #f39c12;
        }
        .alert-low .type {
            color: #27ae60;
        }
        .severity-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            margin-left: 10px;
        }
        .severity-high {
            background: #e74c3c;
            color: white;
        }
        .severity-medium {
            background: #f39c12;
            color: white;
        }
        .severity-low {
            background: #27ae60;
            color: white;
        }
        .alert-card .description {
            color: #555;
            margin: 10px 0;
            line-height: 1.6;
            font-size: 0.95em;
        }
        .alert-card .recommendation {
            background: rgba(0,0,0,0.05);
            padding: 12px;
            border-radius: 5px;
            margin-top: 12px;
            border-left: 3px solid;
            font-style: italic;
        }
        .alert-high .recommendation {
            border-left-color: #e74c3c;
        }
        .alert-medium .recommendation {
            border-left-color: #f39c12;
        }
        .alert-low .recommendation {
            border-left-color: #27ae60;
        }
        .suggestion-card {
            border-left: 5px solid #9b59b6;
        }
        .suggestion-card .category {
            color: #9b59b6;
            font-weight: bold;
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        .suggestion-card p {
            color: #555;
            line-height: 1.6;
        }
        .error {
            background: #e74c3c;
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-size: 1.1em;
        }
        .loading {
            text-align: center;
            color: white;
            font-size: 1.2em;
        }
        .spinner {
            display: inline-block;
            width: 40px;
            height: 40px;
            border: 4px solid rgba(255,255,255,0.3);
            border-top: 4px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .footer {
            text-align: center;
            color: rgba(255,255,255,0.7);
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.2);
        }
        .upload-card {
            background: white;
            border-radius: 10px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            max-width: 600px;
            margin: 0 auto 40px;
        }
        .upload-card h2 {
            color: #667eea;
            margin-bottom: 20px;
        }
        .upload-box {
            border: 3px dashed #667eea;
            border-radius: 10px;
            padding: 40px;
            background: #f8f9ff;
            transition: all 0.3s;
        }
        .upload-box:hover {
            border-color: #764ba2;
            background: #f5f3ff;
        }
        .upload-box.drag-over {
            border-color: #764ba2;
            background: #ede5ff;
        }
        #uploadStatus {
            margin-top: 20px;
        }
        .upload-success {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .upload-error {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
        }
        .upload-loading {
            text-align: center;
            padding: 20px;
        }
        .upload-loading .spinner {
            margin: 0 auto 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 Financial Insights Dashboard</h1>
            <p>Comprehensive Analysis of Your Spending Patterns</p>
        </div>
        
        <div id="uploadSection" style="display: block;">
            <div class="upload-card">
                <h2>📤 Upload HTML Statement</h2>
                <p style="color: #666; margin-bottom: 20px;">Upload your bank or financial statement HTML file to analyze your spending patterns</p>
                
                <div class="upload-box" id="dropZone">
                    <input type="file" id="fileInput" accept=".html,.htm" style="display: none;">
                    <div style="text-align: center; cursor: pointer;">
                        <div style="font-size: 2em; margin-bottom: 10px;">📁</div>
                        <p style="font-weight: bold; color: #667eea; margin-bottom: 5px;">Click to upload or drag and drop</p>
                        <p style="color: #999; font-size: 0.9em;">HTML files only (recommended: Bank statements, Transaction exports)</p>
                    </div>
                </div>
                
                <div id="uploadStatus"></div>
            </div>
        </div>
        
        <div id="content" style="display: none;"></div>
        
        <div class="footer">
            <p>Generated by Financial Insights AI Agent | Last Updated: {{ timestamp }}</p>
        </div>
    </div>

    <script>
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const uploadStatus = document.getElementById('uploadStatus');
        const uploadSection = document.getElementById('uploadSection');
        const contentSection = document.getElementById('content');

        // Click to upload
        dropZone.addEventListener('click', () => fileInput.click());

        // Drag and drop
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('drag-over');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });

        function handleFile(file) {
            // Validate file type
            if (!file.name.endsWith('.html') && !file.name.endsWith('.htm')) {
                uploadStatus.innerHTML = '<div class="upload-error">❌ Please upload an HTML file (.html or .htm)</div>';
                return;
            }

            // Validate file size (max 50MB)
            if (file.size > 50 * 1024 * 1024) {
                uploadStatus.innerHTML = '<div class="upload-error">❌ File too large. Maximum size is 50MB</div>';
                return;
            }

            // Read file
            const reader = new FileReader();
            reader.onload = (e) => {
                const htmlContent = e.target.result;
                uploadStatus.innerHTML = '<div class="upload-loading"><div class="spinner"></div><p>Analyzing your statement...</p></div>';
                
                // Send to server
                fetch('/api/analyze-html', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ htmlContent: htmlContent })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        displayInsights(data);
                        uploadSection.style.display = 'none';
                        contentSection.style.display = 'block';
                        uploadStatus.innerHTML = '<div class="upload-success">✅ Analysis complete!</div>';
                    } else {
                        uploadStatus.innerHTML = `<div class="upload-error">❌ Error: ${data.error || 'Failed to analyze'}</div>`;
                    }
                })
                .catch(error => {
                    uploadStatus.innerHTML = `<div class="upload-error">❌ Error: ${error.message}</div>`;
                });
            };
            reader.readAsText(file);
        }

        function displayInsights(data) {
            const content = contentSection;
            let html = '';

            // Key Insights Section
            if (data.keyInsights && data.keyInsights.length > 0) {
                html += '<div class="section">';
                html += '<h2 class="section-title">🔍 Key Insights</h2>';
                html += '<div class="cards-grid">';
                data.keyInsights.forEach(insight => {
                    html += `
                        <div class="card insight-card">
                            <h3>${insight.title}</h3>
                            <p>${insight.description}</p>
                        </div>
                    `;
                });
                html += '</div></div>';
            }

            // Alerts Section
            if (data.alerts && data.alerts.length > 0) {
                html += '<div class="section">';
                html += '<h2 class="section-title">⚠️ Alerts & Warnings</h2>';
                html += '<div class="cards-grid">';
                data.alerts.forEach(alert => {
                    const severityClass = `alert-${alert.severity}`;
                    html += `
                        <div class="card alert-card ${severityClass}">
                            <div class="type">
                                ${alert.type}
                                <span class="severity-badge severity-${alert.severity}">
                                    ${alert.severity.toUpperCase()}
                                </span>
                            </div>
                            <p class="description">${alert.description}</p>
                            <div class="recommendation">
                                <strong>Recommendation:</strong> ${alert.recommendation}
                            </div>
                        </div>
                    `;
                });
                html += '</div></div>';
            }

            // Suggestions Section
            if (data.suggestions && data.suggestions.length > 0) {
                html += '<div class="section">';
                html += '<h2 class="section-title">💡 Suggestions</h2>';
                html += '<div class="cards-grid">';
                data.suggestions.forEach(suggestion => {
                    html += `
                        <div class="card suggestion-card">
                            <div class="category">${suggestion.category}</div>
                            <p>${suggestion.suggestion}</p>
                        </div>
                    `;
                });
                html += '</div></div>';
            }

            content.innerHTML = html;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Display the insights dashboard"""
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    return render_template_string(INSIGHTS_TEMPLATE, timestamp=timestamp)

@app.route('/api/insights', methods=['GET'])
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

@app.route('/api/analyze-html', methods=['POST'])
def analyze_html():
    """
    Analyze uploaded HTML file for financial insights
    """
    try:
        data = request.get_json()
        html_content = data.get('htmlContent', '')
        
        if not html_content:
            return jsonify({
                "success": False,
                "error": "No HTML content provided"
            }), 400
        
        print("🚀 Analyzing uploaded HTML file...")
        
        # Save HTML temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_html_path = f.name
        
        try:
            # Parse HTML and analyze
            from insights_agent import analyze_html_file
            analysis_result = analyze_html_file(temp_html_path)
            
            if analysis_result is None:
                return jsonify({
                    "success": False,
                    "error": "Failed to analyze HTML file"
                }), 500
            
            # Convert CrewOutput to string
            result_str = str(analysis_result).strip()
            
            # Extract JSON from the result
            try:
                json_start = result_str.find('{')
                json_end = result_str.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = result_str[json_start:json_end]
                    analysis_data = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
                
                # Validate structure
                if "keyInsights" not in analysis_data or "alerts" not in analysis_data or "suggestions" not in analysis_data:
                    raise ValueError("Missing required fields")
                
                return jsonify({
                    "success": True,
                    "keyInsights": analysis_data.get("keyInsights", []),
                    "alerts": analysis_data.get("alerts", []),
                    "suggestions": analysis_data.get("suggestions", [])
                }), 200
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON Parse Error: {str(e)}")
                return jsonify({
                    "success": False,
                    "error": f"Invalid JSON response: {str(e)}"
                }), 500
        finally:
            # Clean up temp file
            if os.path.exists(temp_html_path):
                os.remove(temp_html_path)
        
    except Exception as e:
        print(f"❌ Error analyzing HTML: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Cardano Insights API",
        "version": "1.0.0"
    }), 200

if __name__ == '__main__':
    # Render uses PORT environment variable
    port = int(os.getenv('PORT', 5000))
    # Disable debug mode for production (Render)
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
