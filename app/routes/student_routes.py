from flask import Blueprint, request, jsonify
from app.models.student import Student
from app.utils.database import db
from app.models.room import Room

student_bp = Blueprint("student", __name__)

@student_bp.route("/", methods=["GET"])
def get_students():
    students = Student.query.all()
    return jsonify([{"id": s.id, "name": s.name, "email": s.email} for s in students])

@student_bp.route("/", methods=["POST"])
def create_student():
    data = request.get_json()
    new_student = Student(
        name=data["name"],
        email=data["email"],
        course=data.get("course"),
        hostel_id=data.get("hostel_id"),
        room_id=data.get("room_id")
    )
    db.session.add(new_student)
    db.session.commit()
    return jsonify({"message": "Student created"}), 201

@student_bp.route("/assign-room", methods=["POST"])
def assign_room():
    data = request.get_json()
    student_id = data.get("student_id")
    room_id = data.get("room_id")
    student = Student.query.get(student_id)
    room = Room.query.get(room_id)
    if not student or not room:
        return jsonify({"message": "Student or Room not found"}), 404
    if room.occupied_beds >= room.bed_count:
        return jsonify({"message": "Room is full"}), 400
    # Remove student from previous room if assigned
    if student.room_id:
        prev_room = Room.query.get(student.room_id)
        if prev_room and prev_room.occupied_beds > 0:
            prev_room.occupied_beds -= 1
    # Assign new room
    student.room_id = room.id
    student.hostel_id = room.hostel_id
    room.occupied_beds += 1
    db.session.commit()
    return jsonify({"message": "Room assigned successfully"})

@student_bp.route("/available-rooms", methods=["GET"])
def available_rooms():
    rooms = Room.query.filter(Room.occupied_beds < Room.bed_count).all()
    return jsonify([
        {"id": r.id, "room_number": r.room_number, "hostel_id": r.hostel_id, "available_beds": r.bed_count - r.occupied_beds}
        for r in rooms
    ])

@student_bp.route("/transfer-room", methods=["POST"])
def transfer_room():
    data = request.get_json()
    student_id = data.get("student_id")
    new_room_id = data.get("new_room_id")
    student = Student.query.get(student_id)
    new_room = Room.query.get(new_room_id)
    if not student or not new_room:
        return jsonify({"message": "Student or Room not found"}), 404
    if new_room.occupied_beds >= new_room.bed_count:
        return jsonify({"message": "New room is full"}), 400
    # Remove from old room
    if student.room_id:
        old_room = Room.query.get(student.room_id)
        if old_room and old_room.occupied_beds > 0:
            old_room.occupied_beds -= 1
    # Assign new room
    student.room_id = new_room.id
    student.hostel_id = new_room.hostel_id
    new_room.occupied_beds += 1
    db.session.commit()
    return jsonify({"message": "Room transferred successfully"})

