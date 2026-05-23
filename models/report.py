from models import db
from datetime import datetime
from bson.objectid import ObjectId


class Report:
    """Report model - stored in MongoDB"""
    
    def __init__(self, animal_type, condition, location, description, 
                 priority, reporter_id, reporter_name, reporter_contact, 
                 reporter_email, latitude=None, longitude=None, image_path=None):
        self.animal_type = animal_type
        self.condition = condition
        self.location = location
        self.description = description
        self.priority = priority
        self.latitude = latitude
        self.longitude = longitude
        self.image_path = image_path
        self.status = "Pending"
        self.is_rescued = False
        self.reporter_id = reporter_id
        self.reporter_name = reporter_name
        self.reporter_contact = reporter_contact
        self.reporter_email = reporter_email
        self.rescuer_id = None
        self.rescuer_name = None
        self.rescuer_contact = None
        self.rescuer_email = None
        self.claimed_at = None
        self.completed_at = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.id = None
    
    @staticmethod
    def create(animal_type, condition, location, description, priority,
               reporter_id, reporter_name, reporter_contact, reporter_email,
               latitude=None, longitude=None, image_path=None):
        """Create and save a new report"""
        if db is None:
            raise Exception("Database connection failed")
        
        report = Report(animal_type, condition, location, description, priority,
                        reporter_id, reporter_name, reporter_contact, reporter_email,
                        latitude, longitude, image_path)
        
        report_dict = {
            "animal_type": animal_type,
            "condition": condition,
            "location": location,
            "description": description,
            "priority": priority,
            "latitude": latitude,
            "longitude": longitude,
            "image_path": image_path,
            "status": "Pending",
            "is_rescued": False,
            "reporter_id": reporter_id,
            "reporter_name": reporter_name,
            "reporter_contact": reporter_contact,
            "reporter_email": reporter_email,
            "rescuer_id": None,
            "rescuer_name": None,
            "rescuer_contact": None,
            "rescuer_email": None,
            "claimed_at": None,
            "completed_at": None,
            "created_at": report.created_at,
            "updated_at": report.updated_at
        }
        result = db.reports.insert_one(report_dict)
        report.id = str(result.inserted_id)
        return report
    
    @staticmethod
    def find_by_id(report_id):
        """Find report by ID"""
        if db is None:
            return None
        try:
            report_data = db.reports.find_one({"_id": ObjectId(report_id)})
            if report_data:
                return Report._from_dict(report_data)
        except:
            pass
        return None
    
    @staticmethod
    def find_by_reporter(reporter_id):
        """Find all reports by reporter"""
        if db is None:
            return []
        reports = []
        for report_data in db.reports.find({"reporter_id": reporter_id}).sort("created_at", -1):
            reports.append(Report._from_dict(report_data))
        return reports
    
    @staticmethod
    def find_pending():
        """Find all truly unclaimed pending reports (no rescuer assigned yet)"""
        if db is None:
            return []
        reports = []
        for report_data in db.reports.find({"rescuer_id": None, "is_rescued": False}).sort("created_at", -1):
            reports.append(Report._from_dict(report_data))
        return reports
    
    @staticmethod
    def find_by_rescuer(rescuer_id):
        """Find all reports claimed by a rescuer"""
        if db is None:
            return []
        # Ensure rescuer_id is a string for proper matching
        rescuer_id = str(rescuer_id)
        reports = []
        for report_data in db.reports.find({"rescuer_id": rescuer_id}).sort("claimed_at", -1):
            reports.append(Report._from_dict(report_data))
        return reports
    
    @staticmethod
    def find_all():
        """Find all reports"""
        if db is None:
            return []
        reports = []
        for report_data in db.reports.find().sort("created_at", -1):
            reports.append(Report._from_dict(report_data))
        return reports
    
    @staticmethod
    def _from_dict(report_data):
        """Create Report instance from MongoDB document"""
        report = Report(
            report_data["animal_type"],
            report_data["condition"],
            report_data["location"],
            report_data["description"],
            report_data["priority"],
            report_data["reporter_id"],
            report_data["reporter_name"],
            report_data["reporter_contact"],
            report_data["reporter_email"],
            report_data.get("latitude"),
            report_data.get("longitude"),
            report_data.get("image_path")
        )
        report.id = str(report_data["_id"])
        report.status = report_data.get("status", "Pending")
        report.is_rescued = report_data.get("is_rescued", False)
        report.rescuer_id = report_data.get("rescuer_id")
        report.rescuer_name = report_data.get("rescuer_name")
        report.rescuer_contact = report_data.get("rescuer_contact")
        report.rescuer_email = report_data.get("rescuer_email")
        report.claimed_at = report_data.get("claimed_at")
        report.completed_at = report_data.get("completed_at")
        report.created_at = report_data.get("created_at")
        report.updated_at = report_data.get("updated_at")
        return report
    
    def claim(self, rescuer_id, rescuer_name, rescuer_contact, rescuer_email):
        """Claim this report"""
        if db is None:
            return
        # Ensure rescuer_id is a string
        rescuer_id = str(rescuer_id)
        self.rescuer_id = rescuer_id
        self.rescuer_name = rescuer_name
        self.rescuer_contact = rescuer_contact
        self.rescuer_email = rescuer_email
        self.status = "In Progress"
        self.claimed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        db.reports.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": {
                "rescuer_id": rescuer_id,
                "rescuer_name": rescuer_name,
                "rescuer_contact": rescuer_contact,
                "rescuer_email": rescuer_email,
                "status": "In Progress",
                "claimed_at": self.claimed_at,
                "updated_at": self.updated_at
            }}
        )
    
    def unclaim(self):
        """Unclaim this report"""
        if db is None:
            return
        self.rescuer_id = None
        self.rescuer_name = None
        self.rescuer_contact = None
        self.rescuer_email = None
        self.status = "Pending"
        self.claimed_at = None
        self.updated_at = datetime.utcnow()
        db.reports.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": {
                "rescuer_id": None,
                "rescuer_name": None,
                "rescuer_contact": None,
                "rescuer_email": None,
                "status": "Pending",
                "claimed_at": None,
                "updated_at": self.updated_at
            }}
        )
    
    def mark_rescued(self):
        """Mark this report as rescued"""
        if db is None:
            return
        self.is_rescued = True
        self.status = "Rescued"
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        db.reports.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": {
                "is_rescued": True,
                "status": "Rescued",
                "completed_at": self.completed_at,
                "updated_at": self.updated_at
            }}
        )
    
    def update_status(self, new_status):
        """Update the status of the report"""
        if db is None:
            return
        
        valid_statuses = ["Pending", "In Progress", "Rescued"]
        if new_status not in valid_statuses:
            return False
        
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        # Update is_rescued field based on status
        if new_status == "Rescued":
            self.is_rescued = True
            self.completed_at = datetime.utcnow()
            update_data = {
                "status": new_status,
                "is_rescued": True,
                "completed_at": self.completed_at,
                "updated_at": self.updated_at
            }
        else:
            self.is_rescued = False
            update_data = {
                "status": new_status,
                "is_rescued": False,
                "updated_at": self.updated_at
            }
        
        db.reports.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": update_data}
        )
        return True
    
    def __repr__(self):
        return f"<Report {self.id}: {self.animal_type}>"

