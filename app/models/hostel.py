from app.utils.database import db

class Hostel(db.Model):
    __tablename__ = "hostels"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))  # Male/Female
    capacity = db.Column(db.Integer)
    rooms = db.relationship("Room", backref="hostel", lazy=True)

    def __repr__(self):
        return f"<Hostel {self.name}>"