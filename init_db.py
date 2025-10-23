from app import app, db, bcrypt
from models import User

with app.app_context():
    db.create_all()

    admin = User(
        username="purnimaharshini111@gmail.com",
        password=bcrypt.generate_password_hash("admin123").decode("utf-8"),
        role="admin"
    )
    db.session.add(admin)

    teacher = User(
        username="22a21a6190@swarnandhra.ac.in",
        password=bcrypt.generate_password_hash("teacher123").decode("utf-8"),
        role="teacher"
    )
    db.session.add(teacher)

    student = User(
        username="dasaripurnima@gmail.com",
        password=bcrypt.generate_password_hash("student123").decode("utf-8"),
        role="student",
        admission_no=1001
    )
    db.session.add(student)

    db.session.commit()
    print("✅ Tables created and users added!")