from app.utils.database import db

class Room(db.Model):
    __tablename__ = "rooms"
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), nullable=False)
    hostel_id = db.Column(db.Integer, db.ForeignKey("hostels.id"))
    bed_count = db.Column(db.Integer)
    occupied_beds = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Room {self.room_number}>"