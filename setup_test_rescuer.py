#!/usr/bin/env python3
"""Setup test rescuer and claimed reports for testing status dropdown"""

from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash

# Connect to MongoDB
uri = "mongodb+srv://bangaru:aryabangaru123@cluster0.qxfxb6u.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client["sarrs"]

print("📦 Setting up test rescuer and reports...")

# Create test rescuer
rescuer_id = db.rescuers.insert_one({
    "email": "rescuer@example.com",
    "password_hash": generate_password_hash("rescuer123"),
    "full_name": "Alex Rescuer",
    "phone": "9876543210",
    "specialization": "Dog Rescue",
    "experience_years": 5,
    "is_verified": True,
    "animals_rescued": 0,
    "rating": 4.8,
    "role": "rescuer",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}).inserted_id

print(f"✅ Rescuer created: {rescuer_id}")

# Create a test report
report_id = db.reports.insert_one({
    "animal_type": "Dog",
    "condition": "Injured leg",
    "location": "Downtown Park",
    "description": "Dog with bleeding leg needs help",
    "priority": "High",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "image_path": "uploads/test_dog.jpg",
    "status": "In Progress",
    "is_rescued": False,
    "reporter_id": "reporter123",
    "reporter_name": "John Doe",
    "reporter_contact": "9876543210",
    "reporter_email": "john@example.com",
    "rescuer_id": str(rescuer_id),
    "rescuer_name": "Alex Rescuer",
    "rescuer_contact": "9876543210",
    "rescuer_email": "rescuer@example.com",
    "claimed_at": datetime.utcnow(),
    "completed_at": None,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}).inserted_id

print(f"✅ Test report created: {report_id}")
print(f"\n🔑 Use these credentials to login:")
print(f"   Email: rescuer@example.com")
print(f"   Password: rescuer123")
print(f"\n✨ You should now see the 'MY OPERATIONS' tab with the status dropdown!")
