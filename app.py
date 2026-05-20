from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from functools import wraps
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

app = Flask(__name__)
from pymongo import MongoClient

uri = "mongodb+srv://bangaru:aryabangaru123@cluster0.qxfxb6u.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri)

try:
    client.admin.command('ping')
    print("MongoDB connected successfully ✅")
except Exception as e:
    print("MongoDB connection error ❌", e)

db = client["sarrs"]
collection = db["reports"]

# ==================== CONFIGURATION ====================
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["SECRET_KEY"] = "your_secret_key_change_in_production"

# Email Configuration
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", True)
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "your_email@gmail.com")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "your_password")

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ==================== DATABASE & AUTH SETUP ====================
from models import db
from models.user import User, Rescuer, Admin
from models.report import Report

login_manager = LoginManager(app)
login_manager.login_view = "login"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ==================== USER LOADERS ====================
@login_manager.user_loader
def load_user(user_id):
    """Try to load user from any collection"""
    # Try User
    user = User.find_by_id(user_id)
    if user:
        return user
    # Try Rescuer
    rescuer = Rescuer.find_by_id(user_id)
    if rescuer:
        return rescuer
    # Try Admin
    admin = Admin.find_by_id(user_id)
    return admin

# ==================== DECORATORS ====================
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role != role:
                flash("You don't have permission to access this page", "error")
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def send_email(recipient_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = app.config["MAIL_USERNAME"]
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))
        
        server = smtplib.SMTP(app.config["MAIL_SERVER"], app.config["MAIL_PORT"])
        server.starttls()
        server.login(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# ==================== AUTO-DETECT ROLE ====================
def auto_detect_role(email):
    """Automatically detect user role based on email"""
    # Check in admin collection first (usually admins)
    if Admin.find_by_email(email):
        return "admin"
    # Check in rescuer collection
    if Rescuer.find_by_email(email):
        return "rescuer"
    # Default to user
    if User.find_by_email(email):
        return "user"
    return None

# ==================== AUTH ROUTES ====================
@app.route("/")
def home():
    if current_user.is_authenticated:
        if current_user.role == "user":
            return redirect(url_for("user_dashboard"))
        elif current_user.role == "rescuer":
            return redirect(url_for("rescuer_dashboard"))
        elif current_user.role == "admin":
            return redirect(url_for("admin_dashboard"))
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        # AUTO-DETECT ROLE
        role = auto_detect_role(email)
        
        if not role:
            flash("Email not registered", "error")
            return redirect(url_for("login"))
        
        # Find user by detected role
        user = None
        if role == "user":
            user = User.find_by_email(email)
        elif role == "rescuer":
            user = Rescuer.find_by_email(email)
        elif role == "admin":
            user = Admin.find_by_email(email)
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            return redirect(url_for("home"))
        
        flash("Invalid email or password", "error")
    
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        full_name = request.form.get("full_name")
        phone = request.form.get("phone", "")
        
        # Validation
        if not email or not password or not full_name:
            flash("Please fill in all required fields", "error")
            return redirect(url_for("signup"))
        
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("signup"))
        
        if len(password) < 8:
            flash("Password must be at least 8 characters long", "error")
            return redirect(url_for("signup"))
        
        if not any(char.isupper() for char in password):
            flash("Password must contain at least one uppercase letter (A-Z)", "error")
            return redirect(url_for("signup"))
        
        if not any(char.isdigit() for char in password):
            flash("Password must contain at least one number (0-9)", "error")
            return redirect(url_for("signup"))
        
        # Check if user already exists
        if User.find_by_email(email):
            flash("Email already registered as a user", "error")
            return redirect(url_for("signup"))
        
        if Rescuer.find_by_email(email):
            flash("Email already registered as a rescuer", "error")
            return redirect(url_for("signup"))
        
        if Admin.find_by_email(email):
            flash("Email already registered as an admin", "error")
            return redirect(url_for("signup"))
        
        # Create new user
        try:
            user_id = User.create(
                email=email,
                password=password,
                full_name=full_name,
                phone=phone
            )
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"Error creating account: {str(e)}", "error")
            return redirect(url_for("signup"))
    
    return render_template("signup.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "success")
    return redirect(url_for("home"))

# ==================== USER ROUTES ====================
@app.route("/user/dashboard")
@login_required
@role_required("user")
def user_dashboard():
    reports = Report.find_by_reporter(current_user._id)
    stats = {
        "total_reports": len(reports),
        "rescued": len([r for r in reports if r.is_rescued]),
        "pending": len([r for r in reports if not r.is_rescued]),
    }
    return render_template("user/dashboard.html", reports=reports, stats=stats)

@app.route("/user/report", methods=["GET", "POST"])
@login_required
@role_required("user")
def user_report():
    if request.method == "POST":
        animal_type = request.form.get("animal_type")
        condition = request.form.get("condition")
        location = request.form.get("location")
        description = request.form.get("description")
        priority = request.form.get("priority", "Medium")
        
        latitude = None
        longitude = None
        try:
            lat_str = request.form.get("latitude", "").strip()
            lon_str = request.form.get("longitude", "").strip()
            if lat_str:
                latitude = float(lat_str)
            if lon_str:
                longitude = float(lon_str)
        except (ValueError, TypeError):
            pass

        image_path = None
        if "image" in request.files:
            file = request.files["image"]
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_")
                filename = timestamp + filename
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                image_path = f"uploads/{filename}"

        try:
            new_report = Report.create(
                animal_type=animal_type,
                condition=condition,
                location=location,
                description=description,
                priority=priority,
                latitude=latitude,
                longitude=longitude,
                image_path=image_path,
                reporter_id=current_user._id,
                reporter_name=current_user.full_name,
                reporter_contact=current_user.phone,
                reporter_email=current_user.email,
            )
            flash("Report submitted successfully! Rescuers will help soon.", "success")
            return redirect(url_for("user_dashboard"))
        except Exception as e:
            flash(f"Error submitting report: {str(e)}", "error")
            return redirect(url_for("user_report"))

    return render_template("user/report.html")

# ==================== RESCUER ROUTES ====================
@app.route("/rescuer/dashboard")
@login_required
@role_required("rescuer")
def rescuer_dashboard():
    # Get filter parameters
    location_filter = request.args.get("location", "")
    animal_filter = request.args.get("animal_type", "")
    priority_filter = request.args.get("priority", "")
    
    # Get all pending reports
    pending_reports = Report.find_pending()
    
    # Apply filters
    if location_filter:
        pending_reports = [r for r in pending_reports if location_filter.lower() in r.location.lower()]
    if animal_filter:
        pending_reports = [r for r in pending_reports if animal_filter.lower() in r.animal_type.lower()]
    if priority_filter:
        pending_reports = [r for r in pending_reports if r.priority == priority_filter]
    
    claimed_reports = Report.find_by_rescuer(current_user._id)
    
    stats = {
        "pending": len(pending_reports),
        "claimed": len(claimed_reports),
        "rescued": current_user.animals_rescued,
    }
    
    return render_template("rescuer/dashboard.html", 
                         pending_reports=pending_reports,
                         claimed_reports=claimed_reports,
                         stats=stats)

@app.route("/rescuer/claim/<report_id>", methods=["POST"])
@login_required
@role_required("rescuer")
def claim_rescue(report_id):
    report = Report.find_by_id(report_id)
    
    if not report:
        flash("Report not found", "error")
        return redirect(url_for("rescuer_dashboard"))
    
    if report.rescuer_id is not None:
        flash("This animal has already been claimed", "error")
        return redirect(url_for("rescuer_dashboard"))
    
    report.claim(current_user._id, current_user.full_name, current_user.phone, current_user.email)
    flash("Animal claimed successfully!", "success")
    return redirect(url_for("rescuer_dashboard"))

@app.route("/rescuer/update-status/<report_id>", methods=["POST"])
@login_required
@role_required("rescuer")
def update_rescue_status(report_id):
    report = Report.find_by_id(report_id)
    
    if not report:
        flash("Report not found", "error")
        return redirect(url_for("rescuer_dashboard"))
    
    if report.rescuer_id != current_user._id:
        flash("You can only update your claimed animals", "error")
        return redirect(url_for("rescuer_dashboard"))
    
    is_rescued = request.form.get("is_rescued") == "true"
    
    if is_rescued and not report.is_rescued:
        report.mark_rescued()
        current_user.update_rescue_count()
        
        # Send email to reporter
        email_body = f"""
        <h2>Great News! 🎉</h2>
        <p>Dear {report.reporter_name},</p>
        <p>We have wonderful news! The animal you reported has been successfully rescued!</p>
        <p><strong>Animal Details:</strong></p>
        <ul>
            <li>Type: {report.animal_type}</li>
            <li>Condition: {report.condition}</li>
            <li>Location: {report.location}</li>
        </ul>
        <p><strong>Rescued By:</strong> {current_user.full_name}</p>
        <p><strong>Rescuer Contact:</strong> {current_user.phone}</p>
        <p>Thank you for your immediate reporting and assistance in saving this precious life! 🐾</p>
        <p>Best regards,<br>ResQPaws Team</p>
        """
        send_email(report.reporter_email, "Animal Rescued Successfully! 🎉", email_body)
    
    flash("Status updated successfully!", "success")
    return redirect(url_for("rescuer_dashboard"))

@app.route("/rescuer/unclaim/<report_id>", methods=["POST"])
@login_required
@role_required("rescuer")
def unclaim_rescue(report_id):
    report = Report.find_by_id(report_id)
    
    if not report:
        flash("Report not found", "error")
        return redirect(url_for("rescuer_dashboard"))
    
    if report.rescuer_id != current_user._id:
        flash("You can only unclaim your claimed animals", "error")
        return redirect(url_for("rescuer_dashboard"))
    
    report.unclaim()
    flash("Animal released successfully!", "success")
    return redirect(url_for("rescuer_dashboard"))

# ==================== ADMIN ROUTES ====================
@app.route("/admin/dashboard")
@login_required
@role_required("admin")
def admin_dashboard():
    all_reports = Report.find_all()
    rescuers = Rescuer.find_all()
    
    # Get all statistics
    total_reports = len(all_reports)
    rescued_reports = len([r for r in all_reports if r.is_rescued])
    pending_reports = len([r for r in all_reports if not r.is_rescued])
    total_rescuers = len(rescuers)
    
    # Get rescuers with stats
    rescuer_stats = []
    for rescuer in rescuers:
        claimed_reports = [r for r in all_reports if r.rescuer_id == rescuer._id]
        rescued = len([r for r in claimed_reports if r.is_rescued])
        rescuer_stats.append({
            "id": rescuer._id,
            "name": rescuer.full_name,
            "email": rescuer.email,
            "phone": rescuer.phone,
            "animals_rescued": rescuer.animals_rescued,
            "claimed": len(claimed_reports),
            "rescued": rescued,
            "rating": rescuer.rating
        })
    
    # Get animal type statistics
    animal_stats = {}
    for report in all_reports:
        animal_type = report.animal_type
        if animal_type not in animal_stats:
            animal_stats[animal_type] = {"total": 0, "rescued": 0}
        animal_stats[animal_type]["total"] += 1
        if report.is_rescued:
            animal_stats[animal_type]["rescued"] += 1
    
    # Get priority statistics
    priority_stats = {}
    for report in all_reports:
        priority = report.priority
        if priority not in priority_stats:
            priority_stats[priority] = {"total": 0, "rescued": 0}
        priority_stats[priority]["total"] += 1
        if report.is_rescued:
            priority_stats[priority]["rescued"] += 1
    
    stats = {
        "total_reports": total_reports,
        "rescued_reports": rescued_reports,
        "pending_reports": pending_reports,
        "total_rescuers": total_rescuers,
        "rescue_rate": (rescued_reports / total_reports * 100) if total_reports > 0 else 0
    }
    
    return render_template("admin/dashboard.html", 
                         stats=stats,
                         rescuer_stats=rescuer_stats,
                         animal_stats=animal_stats,
                         priority_stats=priority_stats,
                         all_reports=all_reports)

@app.route("/admin/add-rescuer", methods=["GET", "POST"])
@login_required
@role_required("admin")
def add_rescuer():
    if request.method == "POST":
        email = request.form.get("email")
        full_name = request.form.get("full_name")
        phone = request.form.get("phone")
        experience = request.form.get("experience", "")
        location = request.form.get("location", "")
        password = request.form.get("password", "ResQPaws@123")
        
        # Enhanced password validation
        if len(password) < 8:
            flash("Password must be at least 8 characters", "error")
            return redirect(url_for("add_rescuer"))
        
        if not any(char.isupper() for char in password):
            flash("Password must contain at least one uppercase letter", "error")
            return redirect(url_for("add_rescuer"))
        
        if not any(char.isdigit() for char in password):
            flash("Password must contain at least one number", "error")
            return redirect(url_for("add_rescuer"))
        
        if Rescuer.find_by_email(email):
            flash("Email already exists", "error")
            return redirect(url_for("add_rescuer"))
        
        try:
            rescuer = Rescuer.create(email, full_name, phone, password, experience, location)
            
            # Send email with credentials
            email_body = f"""
            <h2>Welcome to ResQPaws! 🐾</h2>
            <p>Dear {full_name},</p>
            <p>You have been added as a rescuer in the ResQPaws system.</p>
            <p><strong>Login Credentials:</strong></p>
            <ul>
                <li>Email: {email}</li>
                <li>Password: {password}</li>
            </ul>
            <p>Please login and update your password immediately for security.</p>
            <p>Start helping animals in need!</p>
            <p>Best regards,<br>ResQPaws Admin Team</p>
            """
            send_email(email, "Welcome to ResQPaws Rescuer Portal", email_body)
            
            # Successfully added - show success only on admin dashboard, not in flash
            return redirect(url_for("admin_dashboard"))
        except Exception as e:
            # Only show error messages on admin form page
            flash(f"Error adding rescuer: {str(e)}", "error")
            return redirect(url_for("add_rescuer"))
    
    return render_template("admin/add_rescuer.html")

@app.route("/admin/rescuers")
@login_required
@role_required("admin")
def manage_rescuers():
    rescuers = Rescuer.find_all()
    return render_template("admin/manage_rescuers.html", rescuers=rescuers)

@app.route("/admin/reports")
@login_required
@role_required("admin")
def view_all_reports():
    reports = Report.find_all()
    return render_template("admin/view_reports.html", reports=reports)

# ==================== API ROUTES ====================
@app.route("/api/stats")
@login_required
@role_required("admin")
def get_stats():
    all_reports = Report.find_all()
    
    # Timeline data for line chart
    timeline = {}
    for report in all_reports:
        date = report.created_at.strftime("%Y-%m-%d")
        if date not in timeline:
            timeline[date] = {"reports": 0, "rescued": 0}
        timeline[date]["reports"] += 1
        if report.is_rescued:
            timeline[date]["rescued"] += 1
    
    return jsonify({
        "timeline": timeline,
    })

# ==================== DATABASE SEEDING ROUTE ====================
@app.route("/admin/seed-database", methods=["GET", "POST"])
def seed_database():
    """
    Seed database with demo data
    Accessible only to admins or via secret key for initial setup
    """
    # Allow access with secret admin key or if user is admin
    admin_key = request.args.get("key") or request.form.get("key")
    is_authorized = False
    
    if current_user.is_authenticated and current_user.role == "admin":
        is_authorized = True
    elif admin_key == os.getenv("ADMIN_SEED_KEY", "ADMIN_SEED_KEY_NOT_SET"):
        is_authorized = True
    
    if not is_authorized:
        flash("Unauthorized: Admin access required", "error")
        return redirect(url_for("home"))
    
    if request.method == "POST" or request.args.get("confirm") == "true":
        try:
            if db is None:
                flash("Database connection unavailable", "error")
                return redirect(url_for("admin_dashboard"))
            
            # Clear existing data
            db.users.delete_many({})
            db.rescuers.delete_many({})
            db.admins.delete_many({})
            db.reports.delete_many({})
            
            # Create demo users
            users_data = [
                {"email": "user@example.com", "full_name": "John Reporter", "phone": "+1-555-0101", "password": "password123"},
                {"email": "sarah@example.com", "full_name": "Sarah Finder", "phone": "+1-555-0102", "password": "demo1234"},
                {"email": "Mike.chen@example.com", "full_name": "Mike Chen", "phone": "+1-555-0103", "password": "secure123"},
                {"email": "emma.watson@example.com", "full_name": "Emma Watson", "phone": "+1-555-0104", "password": "emma1234"}
            ]
            
            created_users = []
            for user_data in users_data:
                user = User.create(user_data["email"], user_data["full_name"], user_data["phone"], user_data["password"])
                created_users.append(user)
            
            # Create demo rescuers
            rescuers_data = [
                {"email": "alex.rescuer@example.com", "full_name": "Alex Rescuer", "phone": "+1-555-0201", "password": "rescuer123", "experience": "5 years - Bird specialist", "location": "Downtown"},
                {"email": "james.wildlife@example.com", "full_name": "James Wilson", "phone": "+1-555-0202", "password": "james1234", "experience": "8 years - Large animals", "location": "Northern area"},
                {"email": "lisa.rescue@example.com", "full_name": "Lisa Johnson", "phone": "+1-555-0203", "password": "lisa5678", "experience": "6 years - Urban wildlife", "location": "City center"},
                {"email": "david.rescuer@example.com", "full_name": "David Kumar", "phone": "+1-555-0204", "password": "david123", "experience": "10 years - All species", "location": "Metro area"},
                {"email": "sophia.wildlife@example.com", "full_name": "Sophia Martinez", "phone": "+1-555-0205", "password": "sophia99", "experience": "3 years - Small animals", "location": "Community area"}
            ]
            
            created_rescuers = []
            for rescuer_data in rescuers_data:
                rescuer = Rescuer.create(rescuer_data["email"], rescuer_data["full_name"], rescuer_data["phone"], rescuer_data["password"], rescuer_data["experience"], rescuer_data["location"])
                created_rescuers.append(rescuer)
            
            # Create demo admins
            Admin.create("admin@sarrs.com", "Admin Dashboard", "admin1234")
            Admin.create("manager@sarrs.com", "System Manager", "manager123")
            
            # Create demo reports
            reports_data = [
                {"animal_type": "Bird", "condition": "Injured Wing", "location": "Downtown Park", "description": "Eagle with broken wing", "priority": "High", "reporter_idx": 0, "lat": 40.7128, "lon": -74.0060},
                {"animal_type": "Dog", "condition": "Lost/Stray", "location": "Main Street", "description": "Golden Retriever, friendly", "priority": "Medium", "reporter_idx": 1, "lat": 40.7150, "lon": -74.0070},
                {"animal_type": "Cat", "condition": "Stuck/Trapped", "location": "Oak Avenue", "description": "Cat stuck in tree", "priority": "Medium", "reporter_idx": 2, "lat": 40.7200, "lon": -74.0100},
                {"animal_type": "Deer", "condition": "Hit by Vehicle", "location": "Highway 5", "description": "Injured deer on roadside", "priority": "Critical", "reporter_idx": 0, "lat": 40.6800, "lon": -74.0200},
                {"animal_type": "Raccoon", "condition": "Disease Suspected", "location": "Neighborhood", "description": "Disoriented raccoon", "priority": "High", "reporter_idx": 3, "lat": 40.7300, "lon": -74.0150},
                {"animal_type": "Swan", "condition": "Caught in Debris", "location": "Riverside Lake", "description": "Swan tangled in net", "priority": "High", "reporter_idx": 1, "lat": 40.6900, "lon": -74.0180},
                {"animal_type": "Fox", "condition": "Suspected Injury", "location": "Forest Edge", "description": "Fox with limping gait", "priority": "Medium", "reporter_idx": 2, "lat": 40.6750, "lon": -74.0250},
                {"animal_type": "Rabbit", "condition": "Orphaned", "location": "Garden", "description": "Young rabbit without mother", "priority": "Low", "reporter_idx": 3, "lat": 40.7100, "lon": -74.0210}
            ]
            
            for report_data in reports_data:
                reporter = created_users[report_data["reporter_idx"]]
                Report.create(
                    animal_type=report_data["animal_type"],
                    condition=report_data["condition"],
                    location=report_data["location"],
                    description=report_data["description"],
                    priority=report_data["priority"],
                    reporter_id=reporter._id,
                    reporter_name=reporter.full_name,
                    reporter_contact=reporter.phone,
                    reporter_email=reporter.email,
                    latitude=report_data.get("lat"),
                    longitude=report_data.get("lon")
                )
            
            flash(f"Database seeded successfully! Created {len(created_users)} users, {len(created_rescuers)} rescuers, 2 admins, and 8 reports", "success")
            return redirect(url_for("admin_dashboard"))
            
        except Exception as e:
            flash(f"Error seeding database: {str(e)}", "error")
            return redirect(url_for("admin_dashboard"))
    
    # Show confirmation page
    return render_template("admin/seed_database.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
