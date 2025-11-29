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
        description=f"""You are a Senior Financial Analyst. Analyze this COMPLETE financial transaction dataset and provide REAL, DATA-DRIVEN insights.

CRITICAL RULES:
- Return ONLY valid JSON - NO markdown, NO code blocks, NO additional text
- Do NOT generate generic boilerplate insights
- Provide SPECIFIC numbers and amounts from the data
- Categorize ALL transactions based on vendor/description
- Calculate actual spending metrics

TRANSACTION DATA TO ANALYZE:

{csv_content}

TASK - Analyze the data and return ONLY this JSON structure (no other text):

{{
  "keyInsights": [
    {{
      "title": "Total Monthly/Period Spending",
      "description": "Include the exact total amount spent in the period, broken down by top spending categories"
    }},
    {{
      "title": "Top Spending Categories",
      "description": "List the top 5 spending categories with amounts and percentage of total. Example: 'Food & Dining: ₹15,000 (35%), Utilities: ₹8,000 (18%), Travel: ₹6,500 (15%)'"
    }},
    {{
      "title": "Recurring Vendors & Subscription Pattern",
      "description": "Identify vendors appearing multiple times with their transaction count and total spending. Example: 'CMP PPI Wallet Load appears 12 times totaling ₹45,000'"
    }},
    {{
      "title": "High-Value Transactions",
      "description": "List all transactions above ₹5,000 with exact amounts, vendor names, and dates"
    }},
    {{
      "title": "Daily Average Spending",
      "description": "Calculate average daily spend amount"
    }}
  ],
  "alerts": [
    {{
      "type": "Failed Transactions",
      "severity": "medium",
      "description": "List ALL failed transactions with vendor names and amounts",
      "recommendation": "Contact payment provider to resolve failed payment methods"
    }},
    {{
      "type": "Unusually Large Transactions",
      "severity": "medium",
      "description": "Flag any transactions significantly above the average daily spend (more than 5x)",
      "recommendation": "Review and confirm these are legitimate expenses"
    }},
    {{
      "type": "Subscription Costs",
      "severity": "low",
      "description": "Recurring payments identified - list all subscriptions with monthly equivalent costs",
      "recommendation": "Evaluate if all subscriptions are still needed"
    }}
  ],
  "suggestions": [
    {{
      "category": "Expense Optimization",
      "suggestion": "Based on your spending patterns, focus on reducing [CATEGORY] expenses which account for [X]% of your budget"
    }},
    {{
      "category": "Vendor Negotiation",
      "suggestion": "You spend ₹[AMOUNT] with [VENDOR] - consider negotiating bulk rates or finding alternatives"
    }},
    {{
      "category": "Budget Planning",
      "suggestion": "Set monthly budget of ₹[AMOUNT] based on current average and allocate: [CATEGORY 1]: ₹[X], [CATEGORY 2]: ₹[Y], etc."
    }}
  ]
}}

ANALYSIS STEPS:
1. Parse EVERY transaction line carefully
2. Categorize each transaction:
   - Food & Dining (restaurants, cafes, food delivery, grocers)
   - Travel & Transport (flights, trains, uber, taxi, travel sites)
   - Utilities & Bills (electricity, water, insurance, subscriptions)
   - Shopping (retail, online shopping, department stores)
   - Financial Services (banks, wallet loads, investments)
   - Entertainment (movies, games, events)
   - Personal & Health (medical, gym, salon, pharmacy)
   - Other (miscellaneous items)
3. Calculate totals per category
4. Identify failed transactions
5. Identify recurring vendors
6. Calculate daily/monthly averages
7. Find transactions above ₹5,000
8. Return ONLY the JSON object with NO additional text""",
        expected_output="Valid JSON with specific numbers, vendor names, amounts, and calculated metrics - NO generic insights",
        agent=analyzer_agent,
    )

def create_html_analysis_task(html_content: str) -> Task:
    """Create the analysis task for HTML file"""
    return Task(
        description=f"""You are a Senior Financial Analyst. Analyze this HTML financial statement and provide REAL, DATA-DRIVEN insights.

CRITICAL RULES:
- Return ONLY valid JSON - NO markdown, NO code blocks, NO additional text
- Do NOT generate generic boilerplate insights
- Provide SPECIFIC numbers and amounts from the data
- Categorize ALL transactions based on vendor/description
- Calculate actual spending metrics

HTML CONTENT TO ANALYZE:

{html_content}

TASK - Analyze the data and return ONLY this JSON structure (no other text):

{{
  "keyInsights": [
    {{
      "title": "Total Monthly/Period Spending",
      "description": "Include the exact total amount spent in the period, broken down by top spending categories"
    }},
    {{
      "title": "Top Spending Categories",
      "description": "List the top 5 spending categories with amounts and percentage of total. Example: 'Food & Dining: ₹15,000 (35%), Utilities: ₹8,000 (18%), Travel: ₹6,500 (15%)'"
    }},
    {{
      "title": "Recurring Vendors & Subscription Pattern",
      "description": "Identify vendors appearing multiple times with their transaction count and total spending. Example: 'CMP PPI Wallet Load appears 12 times totaling ₹45,000'"
    }},
    {{
      "title": "High-Value Transactions",
      "description": "List all transactions above ₹5,000 with exact amounts, vendor names, and dates"
    }},
    {{
      "title": "Daily Average Spending",
      "description": "Calculate average daily spend amount"
    }}
  ],
  "alerts": [
    {{
      "type": "Failed Transactions",
      "severity": "medium",
      "description": "List ALL failed transactions with vendor names and amounts",
      "recommendation": "Contact payment provider to resolve failed payment methods"
    }},
    {{
      "type": "Unusually Large Transactions",
      "severity": "medium",
      "description": "Flag any transactions significantly above the average daily spend (more than 5x)",
      "recommendation": "Review and confirm these are legitimate expenses"
    }},
    {{
      "type": "Subscription Costs",
      "severity": "low",
      "description": "Recurring payments identified - list all subscriptions with monthly equivalent costs",
      "recommendation": "Evaluate if all subscriptions are still needed"
    }}
  ],
  "suggestions": [
    {{
      "category": "Expense Optimization",
      "suggestion": "Based on your spending patterns, focus on reducing [CATEGORY] expenses which account for [X]% of your budget"
    }},
    {{
      "category": "Vendor Negotiation",
      "suggestion": "You spend ₹[AMOUNT] with [VENDOR] - consider negotiating bulk rates or finding alternatives"
    }},
    {{
      "category": "Budget Planning",
      "suggestion": "Set monthly budget of ₹[AMOUNT] based on current average and allocate: [CATEGORY 1]: ₹[X], [CATEGORY 2]: ₹[Y], etc."
    }}
  ]
}}

ANALYSIS STEPS:
1. Parse EVERY transaction from the HTML carefully
2. Categorize each transaction:
   - Food & Dining (restaurants, cafes, food delivery, grocers)
   - Travel & Transport (flights, trains, uber, taxi, travel sites)
   - Utilities & Bills (electricity, water, insurance, subscriptions)
   - Shopping (retail, online shopping, department stores)
   - Financial Services (banks, wallet loads, investments)
   - Entertainment (movies, games, events)
   - Personal & Health (medical, gym, salon, pharmacy)
   - Other (miscellaneous items)
3. Calculate totals per category
4. Identify failed transactions
5. Identify recurring vendors
6. Calculate daily/monthly averages
7. Find transactions above ₹5,000
8. Return ONLY the JSON object with NO additional text""",
        expected_output="Valid JSON with specific numbers, vendor names, amounts, and calculated metrics - NO generic insights",
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

def analyze_html_file(html_file_path: str):
    """Analyze a user-uploaded HTML file for financial insights"""
    try:
        print(f"[INFO] Analyzing HTML file: {html_file_path}")
        
        # Step 1: Read HTML content with UTF-8 encoding
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"[INFO] HTML file loaded ({len(html_content)} characters)")
        
        # Step 2: Create task with HTML data
        analysis_task = create_html_analysis_task(html_content)
        
        # Step 3: Create crew
        crew = Crew(
            agents=[analyzer_agent],
            tasks=[analysis_task],
            verbose=True,
        )
        
        # Step 4: Run crew
        print("\n[INFO] Running CrewAI Financial Analyzer on HTML with Gemini...")
        print("=" * 60)
        
        result = crew.kickoff()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] HTML ANALYSIS COMPLETE")
        print("=" * 60)
        
        # Extract output from CrewOutput object
        if result:
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
        print(f"[ERROR] Error analyzing HTML file: {str(e)}")
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
