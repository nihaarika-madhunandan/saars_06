from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://bangaru:aryabangaru123@cluster0.qxfxb6u.mongodb.net/sarrs?retryWrites=true&w=majority")

try:
    client = MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000,
        retryWrites=True
    )
    client.admin.command('ping')
    db = client.get_database()
except Exception as e:
    try:
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
    except Exception as e2:
        print(f"[ERROR] MongoDB connection failed: {e2}")
        db = None
