# seed_data.py
import os
from datetime import datetime, date
from app import app, db, bcrypt
from models import User, SchoolRecord, LateRecord

print(f"✅ Using PostgreSQL URL: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    # Create tables
    db.create_all()
    print("✅ Tables created successfully (if not already present)")

    # Clear old data
    db.session.query(LateRecord).delete()
    db.session.query(SchoolRecord).delete()
    db.session.query(User).delete()
    db.session.commit()

    # ------------------------
    # 1️⃣ Add Users
    # ------------------------
    admin = User(username="admin", password=bcrypt.generate_password_hash("admin123").decode("utf-8"), role="admin")
    teacher = User(username="teacher1", password=bcrypt.generate_password_hash("teacher123").decode("utf-8"), role="teacher")
    student = User(username="student1", password=bcrypt.generate_password_hash("student123").decode("utf-8"), role="student", admission_no="A001")

    db.session.add_all([admin, teacher, student])
    db.session.commit()
    print("✅ Admin, teacher, and student users added!")

    # ------------------------
    # 2️⃣ Add School Records
    # ------------------------
    s1 = SchoolRecord(admission_no="A001", student_name="John Doe", class_="10A", parent_email="parent@example.com")
    s2 = SchoolRecord(admission_no="A002", student_name="Jane Smith", class_="10A", parent_email="parent2@example.com")
    db.session.add_all([s1, s2])
    db.session.commit()
    print("✅ School records added!")

    # ------------------------
    # 3️⃣ Add Late Records
    # ------------------------
    lr1 = LateRecord(
        admission_no="A001",
        date=date.today(),
        time=datetime.now().time(),
        reason="Bus delay",
        student_name="John Doe",
        marked_by=teacher.id
    )
    lr2 = LateRecord(
        admission_no="A002",
        date=date.today(),
        time=datetime.now().time(),
        reason="Overslept",
        student_name="Jane Smith",
        marked_by=teacher.id
    )

    db.session.add_all([lr1, lr2])
    db.session.commit()
    print("✅ Late records added!")

print("🎉 Database seeded successfully!")
