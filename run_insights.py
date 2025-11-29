"""
Wrapper to run insights agent and return JSON results
Used by backend API to provide insights endpoint
"""

import sys
import json
from insights_agent import run_insights_agent

if __name__ == "__main__":
    try:
        insights = run_insights_agent()
        print(json.dumps({"success": True, "data": insights}))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)
