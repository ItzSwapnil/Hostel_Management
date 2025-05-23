from app.utils.database import db

class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    course = db.Column(db.String(100))
    hostel_id = db.Column(db.Integer, db.ForeignKey("hostels.id"))
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"))

    def __repr__(self):
        return f"<Student {self.name}>"