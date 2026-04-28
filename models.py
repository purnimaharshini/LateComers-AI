from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = "users"  # ✅ explicit table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    admission_no = db.Column(db.String(20), nullable=True)


class SchoolRecord(db.Model):
    __tablename__ = "schoolrecords"  # ✅ must match the foreign key below
    id = db.Column(db.Integer, primary_key=True)
    admission_no = db.Column(db.String(20), unique=True, nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    class_ = db.Column(db.String(20))
    parent_email = db.Column(db.String(120))


class LateRecord(db.Model):
    __tablename__ = "laterecords"  # ✅ same as what’s used in your SQL queries
    id = db.Column(db.Integer, primary_key=True)
    admission_no = db.Column(
        db.String(20),
        db.ForeignKey("schoolrecords.admission_no"),  # ✅ fixed here
        nullable=False
    )
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    reason = db.Column(db.String(200))
    student_name = db.Column(db.String(100))
    marked_by = db.Column(db.Integer, db.ForeignKey("users.id"))
