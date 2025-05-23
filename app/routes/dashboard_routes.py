from flask import Blueprint, jsonify, request
from app.models.student import Student
from app.models.hostel import Hostel
from app.models.room import Room
from app.models.complaint import Complaint
from app.routes.auth_routes import jwt_required

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/", methods=["GET"])
@jwt_required
def dashboard():
    stats = {
        "total_students": Student.query.count(),
        "total_hostels": Hostel.query.count(),
        "total_rooms": Room.query.count(),
        "total_complaints": Complaint.query.count(),
    }
    return jsonify(stats)

@dashboard_bp.route("/details", methods=["GET"])
@jwt_required
def dashboard_details():
    recent_complaints = Complaint.query.order_by(Complaint.timestamp.desc()).limit(5).all()
    available_rooms = Room.query.filter(Room.occupied_beds < Room.bed_count).all()
    return jsonify({
        "recent_complaints": [
            {"id": c.id, "student_id": c.student_id, "status": c.status, "timestamp": c.timestamp} for c in recent_complaints
        ],
        "available_rooms": [
            {"id": r.id, "room_number": r.room_number, "hostel_id": r.hostel_id, "available_beds": r.bed_count - r.occupied_beds} for r in available_rooms
        ]
    })
