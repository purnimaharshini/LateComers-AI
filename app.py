import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv

# Load .env first
load_dotenv()

app = Flask(__name__)

# ✅ Load configuration from config.py
app.config.from_object('config.Config')

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

# Import routes after initializing app & db
import routes

if __name__ == "__main__":
    app.run(debug=True)
