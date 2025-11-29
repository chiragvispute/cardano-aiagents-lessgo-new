#!/usr/bin/env python3
"""
Parse Google Pay HTML files and output transactions as JSON
This is called from Node.js backend
"""
import sys
import json
import re
import pandas as pd
from typing import List, Dict, Optional, Tuple

class FlexibleGooglePayParser:
    """Parser for Google Pay HTML exports with flexible regex-based extraction"""
    
    STANDARD_COLUMNS = [
        'timestamp', 'amount', 'currency', 'recipient', 'payment_method',
        'account_number', 'transaction_id', 'status', 'product', 'wallet'
    ]
    
    def __init__(self):
        self.patterns = {
            'amount': r'(₹|€|\$|£)\s*([\d,]+\.?\d*)',
            'recipient': r'(?:Paid|Sent|Received)\s+[₹€$£][\d.,]+\s+(?:to|from|by)\s+([^\n<]+?)(?:\s+using|\s+via|<br|\n|$)',
            'payment_method': r'(?:using|via|through)\s+([^<\n]+?)(?:\s+(?:XXXXXXX|XXXX)|<br|\n|$)',
            'account_number': r'(XXXXXXX[A-Z0-9]{6,}|[A-Z0-9]{4}XXXXXXX[A-Z0-9]{4}|XXX\d+)',
            'status': r'(?:Status|State)[:\s]*(?:</b><br\s*/>&emsp;)?(\w+)(?:<br|$)',
            'timestamp_format1': r'(\d{1,2}\s+\w+,\s+\d{4},\s+\d{1,2}:\d{2}:\d{2}\s+(?:AM|PM)\s+GMT[+-]\d{2}:\d{2})',
            'timestamp_format2': r'(\d{1,2}\s+\w+\s+\d{4},\s+\d{1,2}:\d{2}:\d{2}\s+GMT[+-]\d{2}:\d{2})',
        }
    
    def extract_amount(self, text: str) -> Tuple[Optional[float], Optional[str]]:
        match = re.search(self.patterns['amount'], text)
        if match:
            currency_map = {'₹': 'INR', '€': 'EUR', '$': 'USD', '£': 'GBP'}
            try:
                amount = float(match.group(2).replace(',', ''))
                currency = currency_map.get(match.group(1), match.group(1))
                return amount, currency
            except ValueError:
                pass
        return None, None
    
    def extract_recipient(self, text: str) -> Optional[str]:
        match = re.search(self.patterns['recipient'], text, re.IGNORECASE)
        if match:
            recipient = match.group(1).strip()
            recipient = re.sub(r'\s*<br\s*/?>\s*', ' ', recipient)
            recipient = re.sub(r'&emsp;', '', recipient)
            recipient = re.sub(r'\s+(using|via|through).*', '', recipient, flags=re.IGNORECASE)
            return recipient.strip() if recipient else None
        return None
    
    def extract_payment_method(self, text: str) -> Optional[str]:
        match = re.search(self.patterns['payment_method'], text)
        if match:
            method = match.group(1).strip()
            method = re.sub(r'\s+XXXXXXX[A-Z0-9]{6,}', '', method)
            method = re.sub(r'\s+[A-Z0-9]{4}XXXXXXX[A-Z0-9]{4}', '', method)
            method = ' '.join(method.split())
            return method if method else None
        return None
    
    def extract_account_number(self, text: str) -> Optional[str]:
        match = re.search(self.patterns['account_number'], text)
        return match.group(1).strip() if match else None
    
    def extract_transaction_id(self, text: str) -> Optional[str]:
        match = re.search(r'<b>Details:</b\s*><br\s*/>&emsp;([A-Za-z0-9]+)', text)
        if match:
            tid = match.group(1).strip()
            return tid if len(tid) > 3 else None
        
        match = re.search(r'Details\s*:?<br\s*/>&emsp;([A-Za-z0-9]{6,})', text)
        if match:
            return match.group(1).strip()
        
        return None
    
    def extract_status(self, text: str) -> Optional[str]:
        statuses = ['Completed', 'Pending', 'Failed', 'Cancelled', 'Processing']
        for status in statuses:
            if status in text:
                return status
        
        match = re.search(self.patterns['status'], text)
        return match.group(1).strip() if match else None
    
    def extract_timestamp(self, text: str) -> Optional[str]:
        # Try format: "Jul 28, 2024, 4:24:58 PM GMT+05:30"
        match = re.search(r'(\w+)\s+(\d{1,2}),\s+(\d{4}),\s+(\d{1,2}):(\d{2}):(\d{2})\s+(AM|PM)', text)
        if match:
            month_str, day, year, hour, minute, second, ampm = match.groups()
            hour = int(hour)
            if ampm == 'PM' and hour != 12:
                hour += 12
            elif ampm == 'AM' and hour == 12:
                hour = 0
            month_num = self._month_to_num(month_str)
            return f"{year}-{month_num:02d}-{int(day):02d}T{int(hour):02d}:{minute}:{second}Z"
        
        # Try format: "Jul 28, 2024, 4:25:32 PM"
        match = re.search(r'(\w+)\s+(\d{1,2}),\s+(\d{4}),\s+(\d{1,2}):(\d{2}):(\d{2})\s+(AM|PM)', text)
        if match:
            month_str, day, year, hour, minute, second, ampm = match.groups()
            hour = int(hour)
            if ampm == 'PM' and hour != 12:
                hour += 12
            elif ampm == 'AM' and hour == 12:
                hour = 0
            month_num = self._month_to_num(month_str)
            return f"{year}-{month_num:02d}-{int(day):02d}T{int(hour):02d}:{minute}:{second}Z"
        
        # Try simpler format: "Jul 28, 2024"
        match = re.search(r'(\w+)\s+(\d{1,2}),\s+(\d{4})', text)
        if match:
            month_str, day, year = match.groups()
            month_num = self._month_to_num(month_str)
            return f"{year}-{month_num:02d}-{int(day):02d}T00:00:00Z"
        
        return None
    
    def _normalize_timestamp(self, ts: str) -> str:
        ts = re.sub(r'&emsp;', '', ts).strip()
        
        match = re.search(r'(\w+)\s+(\d{1,2}),\s+(\d{4}),\s+(\d{1,2}):(\d{2}):(\d{2})\s+(AM|PM)', ts)
        if match:
            month_str, day, year, hour, minute, second, ampm = match.groups()
            hour = int(hour)
            if ampm == 'PM' and hour != 12:
                hour += 12
            elif ampm == 'AM' and hour == 12:
                hour = 0
            month_num = self._month_to_num(month_str)
            return f"{year}-{month_num:02d}-{int(day):02d} {int(hour):02d}:{minute}:{second}"
        
        match = re.search(r'(\d{1,2})\s+(\w+)\s+(\d{4}),\s+(\d{1,2}):(\d{2}):(\d{2})', ts)
        if match:
            day, month_str, year, hour, minute, second = match.groups()
            month_num = self._month_to_num(month_str)
            return f"{year}-{month_num:02d}-{int(day):02d} {int(hour):02d}:{minute}:{second}"
        
        return ts
    
    @staticmethod
    def _month_to_num(month_str: str) -> int:
        months = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                  'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
        return months.get(month_str, 1)
    
    def extract_product(self, text: str) -> Optional[str]:
        match = re.search(r'<b>Products:</b><br\s*/>&emsp;([^\n<]+)', text)
        if match:
            product = match.group(1).strip()
            product = re.sub(r'<br\s*/?>', '', product)
            product = re.sub(r'&emsp;', '', product)
            product = product.split('<')[0].strip()
            return product if product else None
        
        return 'Google Pay' if 'Google Pay' in text else None
    
    def extract_from_transaction_block(self, block: str) -> Optional[Dict]:
        if not re.search(r'(Paid|Sent|Received|Credited)', block):
            return None
        
        extracted = {
            'timestamp': None,
            'amount': None,
            'currency': None,
            'recipient': None,
            'payment_method': None,
            'account_number': None,
            'transaction_id': None,
            'status': None,
            'product': None,
            'wallet': None,
        }
        
        extracted['amount'], extracted['currency'] = self.extract_amount(block)
        extracted['recipient'] = self.extract_recipient(block)
        extracted['payment_method'] = self.extract_payment_method(block)
        extracted['account_number'] = self.extract_account_number(block)
        extracted['transaction_id'] = self.extract_transaction_id(block)
        extracted['status'] = self.extract_status(block)
        extracted['timestamp'] = self.extract_timestamp(block)
        extracted['product'] = self.extract_product(block)
        extracted['wallet'] = extracted['product']
        
        return extracted if extracted['amount'] is not None else None
    
    def parse_html_file(self, filepath: str) -> List[Dict]:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        transactions = []
        
        blocks = re.findall(
            r'<div class="outer-cell[^>]*>.*?(?=<div class="outer-cell|$)',
            content, re.DOTALL
        )
        
        if not blocks or len(blocks) < 2:
            blocks = re.findall(
                r'<p class="mdl-typography--title">Google Pay<br /></p>.*?(?=<p class="mdl-typography--title"|$)',
                content, re.DOTALL
            )
        
        if not blocks or len(blocks) < 2:
            blocks = re.findall(
                r'(?:Paid|Sent|Received|Credited)\s+[₹€$£][\d.,]+.*?(?:GMT[+-]\d{2}:\d{2})',
                content, re.DOTALL
            )
        
        for block in blocks:
            try:
                transaction = self.extract_from_transaction_block(block)
                if transaction:
                    transactions.append(transaction)
            except Exception:
                continue
        
        return transactions


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No HTML file path provided"}))
        sys.exit(1)
    
    html_filepath = sys.argv[1]
    
    try:
        parser = FlexibleGooglePayParser()
        transactions = parser.parse_html_file(html_filepath)
        
        # Output as JSON for Node.js to consume
        print(json.dumps(transactions))
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
