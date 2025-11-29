"""
Insights Agent using CrewAI with Gemini LLM
Analyzes transaction data and provides financial insights, alerts, and suggestions
"""

import os
import json
import subprocess
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from crewai.llm import LLM

# Load environment variables
load_dotenv()

# Initialize Gemini API key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Set Gemini as the default LLM for CrewAI
os.environ['GEMINI_API_KEY'] = GEMINI_API_KEY

# Create Gemini LLM instance
gemini_llm = LLM(
    model="gemini-2.0-flash",
    api_key=GEMINI_API_KEY
)

# ============================
# 📊 HELPER FUNCTIONS
# ============================

def export_transactions_to_csv():
    """Run the export script to get fresh transaction data"""
    try:
        export_script = os.path.join(os.path.dirname(__file__), 'export_transactions_to_csv.py')
        print(f"[DEBUG] Export script path: {export_script}")
        print(f"[DEBUG] Export script exists: {os.path.exists(export_script)}")
        
        result = subprocess.run(
            ['python', export_script],
            capture_output=True,
            text=True,
            timeout=30
        )
        print(f"[DEBUG] Export process return code: {result.returncode}")
        print(f"[DEBUG] Export stdout:\n{result.stdout}")
        if result.stderr:
            print(f"[DEBUG] Export stderr:\n{result.stderr}")
        
        if result.returncode != 0:
            print(f"[ERROR] Export script error: {result.stderr}")
            return None
        
        # CSV is generated as transactions_export.csv
        csv_path = os.path.join(os.path.dirname(__file__), 'transactions_export.csv')
        print(f"[DEBUG] Looking for CSV at: {csv_path}")
        print(f"[DEBUG] CSV exists: {os.path.exists(csv_path)}")
        
        if os.path.exists(csv_path):
            print(f"[DEBUG] CSV file size: {os.path.getsize(csv_path)} bytes")
            return csv_path
        else:
            print("[ERROR] CSV file not generated")
            return None
    except Exception as e:
        print(f"[ERROR] Error exporting transactions: {e}")
        import traceback
        traceback.print_exc()
        return None

# ============================
# 👤 AGENT
# ============================

analyzer_agent = Agent(
    role="Senior Financial Analyst",
    goal="Analyze complete expense data and provide comprehensive financial insights, alerts, and suggestions.",
    backstory=(
        "You are an expert financial analyst who examines every single transaction "
        "in expense reports to identify patterns, risks, and opportunities. "
        "You excel at detecting spending anomalies and providing actionable recommendations."
    ),
    llm=gemini_llm,
    verbose=True
)

# ============================
# 🎯 TASK
# ============================

def create_analysis_task(csv_content: str) -> Task:
    """Create the analysis task with CSV data embedded"""
    return Task(
        description=f"""Analyze this COMPLETE financial dataset and provide comprehensive insights in STRICT JSON format ONLY.

Return ONLY valid JSON with this exact structure - NO markdown, NO text, ONLY JSON:

{{
  "keyInsights": [
    {{"title": "string", "description": "string"}},
    {{"title": "string", "description": "string"}},
    {{"title": "string", "description": "string"}}
  ],
  "alerts": [
    {{"type": "string", "severity": "high|medium|low", "description": "string", "recommendation": "string"}},
    {{"type": "string", "severity": "high|medium|low", "description": "string", "recommendation": "string"}}
  ],
  "suggestions": [
    {{"category": "string", "suggestion": "string"}},
    {{"category": "string", "suggestion": "string"}}
  ]
}}

COMPLETE TRANSACTION DATA:

{csv_content}

Analyze EVERY transaction. Return ONLY the JSON object above with no additional text, no markdown formatting, no explanations.""",
        expected_output="Valid JSON object with keyInsights, alerts, and suggestions arrays.",
        agent=analyzer_agent,
    )

# ============================
# 🚀 CREW & RUN
# ============================

def analyze_spending_patterns():
    """Main function to run the CrewAI financial analyzer"""
    try:
        # Step 1: Export transactions
        print("[INFO] Exporting transactions...")
        csv_path = export_transactions_to_csv()
        
        if not csv_path:
            print("[ERROR] Failed to export transactions")
            return None
        
        print(f"[INFO] Transactions exported to: {csv_path}")
        
        # Step 2: Read CSV content
        with open(csv_path, 'r', encoding='utf-8') as f:
            csv_content = f.read()
        
        print(f"[INFO] CSV data loaded ({len(csv_content)} characters)")
        
        # Step 3: Create task with CSV data
        analysis_task = create_analysis_task(csv_content)
        
        # Step 4: Create crew
        crew = Crew(
            agents=[analyzer_agent],
            tasks=[analysis_task],
            verbose=True,
        )
        
        # Step 5: Run crew
        print("\n[INFO] Running CrewAI Financial Analyzer with Gemini...")
        print("=" * 60)
        
        result = crew.kickoff()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] FINANCIAL ANALYSIS COMPLETE")
        print("=" * 60)
        
        # Extract output from CrewOutput object
        if result:
            # CrewOutput has a 'raw' attribute or convert to string
            if hasattr(result, 'raw'):
                output = result.raw
            elif hasattr(result, 'output'):
                output = result.output
            else:
                output = str(result)
            
            print(f"[INFO] Output type: {type(output)}")
            print(f"[INFO] Output length: {len(str(output))}")
            return output
        
        return None
        
    except Exception as e:
        print(f"[ERROR] Error running insights agent: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def run_insights_agent():
    """Entry point for running the insights agent"""
    try:
        result = analyze_spending_patterns()
        
        if result:
            final_output = {
                "success": True,
                "data": str(result)
            }
            return json.dumps(final_output, indent=2)
        else:
            print("[ERROR] Failed to generate insights")
            return json.dumps({"success": False, "error": "Failed to generate insights"})
            
    except Exception as e:
        print(f"[ERROR] Error in run_insights_agent: {str(e)}")
        import traceback
        traceback.print_exc()
        return json.dumps({"success": False, "error": str(e)})

if __name__ == "__main__":
    insights = run_insights_agent()
    print(insights)
