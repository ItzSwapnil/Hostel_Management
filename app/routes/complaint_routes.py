from flask import Blueprint, request, jsonify
from app.models.complaint import Complaint
from app.utils.database import db
from app.routes.auth_routes import jwt_required

complaint_bp = Blueprint("complaint", __name__)

@complaint_bp.route("/", methods=["GET"])
def get_complaints():
    complaints = Complaint.query.all()
    return jsonify([{"id": c.id, "student_id": c.student_id, "status": c.status} for c in complaints])

@complaint_bp.route("/", methods=["POST"])
def create_complaint():
    data = request.get_json()
    new_complaint = Complaint(
        student_id=data["student_id"],
        description=data["description"]
    )
    db.session.add(new_complaint)
    db.session.commit()
    return jsonify({"message": "Complaint submitted"}), 201

@complaint_bp.route("/<int:complaint_id>/resolve", methods=["POST"])
@jwt_required
def resolve_complaint(complaint_id):
    # Only admin can resolve
    if request.user.get("role") != "admin":
        return jsonify({"message": "Admin access required"}), 403
    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({"message": "Complaint not found"}), 404
    complaint.status = "Resolved"
    db.session.commit()
    return jsonify({"message": "Complaint marked as resolved"})

@complaint_bp.route("/<int:complaint_id>", methods=["PATCH"])
@jwt_required
def update_complaint_status(complaint_id):
    # Only admin can update
    if request.user.get("role") != "admin":
        return jsonify({"message": "Admin access required"}), 403
    data = request.get_json()
    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({"message": "Complaint not found"}), 404
    if "status" in data:
        complaint.status = data["status"]
    db.session.commit()
    return jsonify({"message": "Complaint status updated"})

