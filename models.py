from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    admission_no = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

class SchoolRecord(db.Model):
    __tablename__ = "schoolrecords"
    admission_no = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(120), nullable=False)
    class_ = db.Column("class", db.String(20))
    section = db.Column(db.String(10))
    parent_email = db.Column(db.String(120))
    parent_phone = db.Column(db.String(30))

class LateRecord(db.Model):
    __tablename__ = "laterecords"
    id = db.Column(db.Integer, primary_key=True)
    admission_no = db.Column(db.Integer, db.ForeignKey("schoolrecords.admission_no"))
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    reason = db.Column(db.String(255))
    student_name = db.Column(db.String(120))
    marked_by = db.Column(db.Integer, db.ForeignKey("users.id"))
