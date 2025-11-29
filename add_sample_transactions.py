import pymongo
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/cardano-hackathon')
DB_NAME = 'cardano-hackathon'

def add_sample_transactions():
    """
    Add sample transactions to MongoDB for testing
    """
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        
        # Check if users collection has any users
        users = db['users'].find_one({})
        if not users:
            print("No users found. Creating a test user...")
            user = {
                'name': 'Test User',
                'email': 'test@example.com',
                'walletAddress': 'addr_test123',
                'createdAt': datetime.now()
            }
            result = db['users'].insert_one(user)
            user_id = result.inserted_id
        else:
            user_id = users['_id']
        
        print(f"Using user ID: {user_id}")
        
        # Sample transactions
        sample_transactions = [
            {
                'userId': user_id,
                'type': 'expense',
                'amount': 150.00,
                'currency': 'INR',
                'category': 'Food & Dining',
                'description': 'Lunch at restaurant',
                'recipient': 'Starbucks',
                'paymentMethod': 'Credit Card',
                'accountNumber': 'XXXX1234',
                'transactionId': 'TXN001',
                'status': 'Completed',
                'date': datetime.now() - timedelta(days=5),
                'UPI': 1,
                'UserInput': 0,
                'tags': ['food', 'dining']
            },
            {
                'userId': user_id,
                'type': 'expense',
                'amount': 500.00,
                'currency': 'INR',
                'category': 'Shopping',
                'description': 'Grocery shopping',
                'recipient': 'Big Bazaar',
                'paymentMethod': 'UPI',
                'accountNumber': 'XXXX5678',
                'transactionId': 'TXN002',
                'status': 'Completed',
                'date': datetime.now() - timedelta(days=3),
                'UPI': 1,
                'UserInput': 0,
                'tags': ['shopping', 'groceries']
            },
            {
                'userId': user_id,
                'type': 'income',
                'amount': 50000.00,
                'currency': 'INR',
                'category': 'Salary',
                'description': 'Monthly salary',
                'date': datetime.now() - timedelta(days=1),
                'UPI': 0,
                'UserInput': 1,
                'tags': ['salary', 'income']
            },
            {
                'userId': user_id,
                'type': 'expense',
                'amount': 1200.00,
                'currency': 'INR',
                'category': 'Transportation',
                'description': 'Uber ride',
                'recipient': 'Uber',
                'paymentMethod': 'Bank Account',
                'accountNumber': 'XXXX9999',
                'transactionId': 'TXN003',
                'status': 'Pending',
                'date': datetime.now(),
                'UPI': 0,
                'UserInput': 1,
                'tags': ['transport']
            }
        ]
        
        # Insert sample transactions
        result = db['transactions'].insert_many(sample_transactions)
        print(f"✅ Inserted {len(result.inserted_ids)} sample transactions")
        
        # Show what was inserted
        count = db['transactions'].count_documents({})
        print(f"Total transactions in database: {count}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise

if __name__ == '__main__':
    add_sample_transactions()
