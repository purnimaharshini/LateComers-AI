import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# ✅ Load config from config.py
app.config.from_object('config.Config')

# ✅ Initialize database
db = SQLAlchemy(app)

# ✅ Create tables if not existing (only for first deploy)
with app.app_context():
    from models import User  # import models inside app context
    db.create_all()
    print("✅ Database tables created successfully (if not existing)")

# Initialize other extensions
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

# ✅ Import routes at the end to avoid circular imports
import routes

if __name__ == "__main__":
    app.run(debug=True)
