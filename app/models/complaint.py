from app.utils.database import db

class Complaint(db.Model):
    __tablename__ = "complaints"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="Pending")  # Pending/Resolved
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f"<Complaint {self.id}>"