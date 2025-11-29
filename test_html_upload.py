#!/usr/bin/env python3
"""
Test script to simulate what the backend does when receiving HTML
"""
import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from parse_html_to_json import FlexibleGooglePayParser

def test_html_upload_simulation():
    """Simulate what happens when backend receives HTML content"""
    html_file = Path(__file__).parent / "My Activity.html"
    
    if not html_file.exists():
        print(f"ERROR: {html_file} not found")
        return
    
    print(f"Testing HTML file: {html_file}")
    print(f"File size: {html_file.stat().st_size} bytes")
    
    # Read the HTML content (simulating frontend reading it)
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print(f"HTML content loaded: {len(html_content)} characters")
    print(f"HTML starts with: {html_content[:100]}...")
    print(f"HTML contains 'Sent': {html_content.count('Sent')} occurrences")
    print(f"HTML contains 'Received': {html_content.count('Received')} occurrences")
    
    # Now simulate the backend parsing it
    print("\n--- Simulating Backend Parsing ---")
    parser = FlexibleGooglePayParser()
    
    # This is what htmlParser.js does - writes to temp file then calls Python
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        temp_path = f.name
    
    print(f"Temp file created: {temp_path}")
    print(f"Temp file size: {Path(temp_path).stat().st_size} bytes")
    
    # Parse
    transactions = parser.parse_html_file(temp_path)
    print(f"\nTransactions found: {len(transactions)}")
    
    if transactions:
        print(f"First transaction: {json.dumps(transactions[0], indent=2)}")
        print(f"\nSample amounts: {[tx['amount'] for tx in transactions[:5]]}")
    else:
        print("NO TRANSACTIONS FOUND!")
        print("Checking HTML for transaction markers...")
        print(f"Contains '₹': {'₹' in html_content}")
        print(f"Contains 'Sent': {'Sent' in html_content}")
        print(f"Contains 'Received': {'Received' in html_content}")
    
    # Clean up
    import os
    os.unlink(temp_path)

if __name__ == '__main__':
    test_html_upload_simulation()
