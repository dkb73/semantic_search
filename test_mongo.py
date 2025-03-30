from pymongo import MongoClient
from config import MONGO_URI

try:
    client = MongoClient(MONGO_URI)
    db = client["hostelDB"]  # Replace with your actual database name
    print("✅ Successfully connected to MongoDB Atlas!")

    # List collections to check if the database has data
    collections = db.list_collection_names()
    print("Collections:", collections)

except Exception as e:
    print("❌ Connection failed:", e)
