import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# 🧩 Get DATABASE_URL from Render environment or .env
database_url = os.getenv("DATABASE_URL")

# Render sometimes provides postgres://, SQLAlchemy needs postgresql+psycopg2://
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)

# ✅ Use DATABASE_URL if available, otherwise fallback to config.py
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    from config import Config
    app.config.from_object(Config)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 🧩 Logging to confirm which DB is in use
app.logger.setLevel(logging.INFO)
app.logger.info("✅ Using SQLALCHEMY_DATABASE_URI = %s", app.config.get("SQLALCHEMY_DATABASE_URI"))

db = SQLAlchemy(app)

# ✅ Create tables automatically on startup
with app.app_context():
    from models import User
    db.create_all()
    print("✅ Tables created successfully (if not already present)")

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

import routes

if __name__ == "__main__":
    app.run(debug=True)
