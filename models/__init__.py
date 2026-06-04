from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI") or "mongodb+srv://bangaru:ZWniXEe6tfT8LvX0@cluster0.qxfxb6u.mongodb.net/sarrs?retryWrites=true&w=majority"

try:
    # Connect to MongoDB Atlas
    # tlsInsecure=true in the URI disables certificate verification for Windows SSL compatibility
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
        retryWrites=True
    )
    # Test connection
    client.admin.command('ping')
    db = client.get_database()
    print("[SUCCESS] MongoDB Atlas connected successfully!")
except Exception as e:
    print(f"[ERROR] MongoDB Connection Error: {e}")
    try:
        client.close()
    except Exception:
        pass
    print("[INFO] Retrying with extended timeout...")
    try:
        # Fallback: try with extended timeouts
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            retryWrites=True,
            maxPoolSize=10,
            minPoolSize=5
        )
        client.admin.command('ping')
        db = client.get_database()
        print("[SUCCESS] MongoDB Atlas connected with extended timeout!")
    except Exception as e2:
        print(f"[ERROR] Final error: {e2}")
        try:
            client.close()
        except Exception:
            pass
        print("[WARNING] Live database connection failed. Falling back to mongomock...")
        try:
            import mongomock
            client = mongomock.MongoClient()
            db = client.get_database("sarrs")
            print("[SUCCESS] Using in-memory mock MongoDB (mongomock) for demo mode")
        except Exception as e3:
            print(f"[ERROR] Failed to initialize mongomock: {e3}")
            db = None
