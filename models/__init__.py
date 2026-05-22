from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGODB_URI = "mongodb+srv://bangaru:aryabangaru123@cluster0.qxfxb6u.mongodb.net/sarrs?retryWrites=true&w=majority"

try:
    # Connect to MongoDB Atlas
    # tlsInsecure=true in the URI disables certificate verification for Windows SSL compatibility
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000,
        retryWrites=True
    )
    # Test connection
    client.admin.command('ping')
    db = client.get_database()
    print("[SUCCESS] MongoDB Atlas connected successfully!")
except Exception as e:
    print(f"[ERROR] MongoDB Connection Error: {e}")
    print("[INFO] Retrying with extended timeout...")
    try:
        # Fallback: try with extended timeouts
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=20000,
            connectTimeoutMS=20000,
            socketTimeoutMS=20000,
            retryWrites=True,
            maxPoolSize=10,
            minPoolSize=5
        )
        client.admin.command('ping')
        db = client.get_database()
        print("[SUCCESS] MongoDB Atlas connected with extended timeout!")
    except Exception as e2:
        print(f"[ERROR] Final error: {e2}")
        print("[WARNING] Running in offline mode - database unavailable")
        db = None

