from app import app, db, bcrypt
from models import User
with app.app_context():
    pw = bcrypt.generate_password_hash("admin123").decode('utf-8')
    admin = User(username="admin@example.com", password=pw, role="admin")
    db.session.add(admin)
    db.session.commit()
    print("admin created")
