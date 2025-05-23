from flask import Blueprint, request, jsonify
from app.models.hostel import Hostel
from app.utils.database import db

hostel_bp = Blueprint("hostel", __name__)

@hostel_bp.route("/", methods=["GET"])
def get_hostels():
    hostels = Hostel.query.all()
    return jsonify([{"id": h.id, "name": h.name, "type": h.type} for h in hostels])

@hostel_bp.route("/", methods=["POST"])
def create_hostel():
    data = request.get_json()
    new_hostel = Hostel(
        name=data["name"],
        type=data["type"],
        capacity=data["capacity"]
    )
    db.session.add(new_hostel)
    db.session.commit()
    return jsonify({"message": "Hostel created"}), 201