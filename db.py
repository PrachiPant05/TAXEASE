# db.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGODB_URI")

try:
    client = MongoClient(mongo_uri)
    db = client.get_database()  # Defaults to 'taxdb' as per URI
    print("✅ Connected to MongoDB Atlas!")
    print("📦 Available collections:", db.list_collection_names())
except Exception as e:
    print("❌ Connection failed:", e)
