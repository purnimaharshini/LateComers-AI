import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Config:
    # --- Flask Core Config ---
    SECRET_KEY = os.getenv("SECRET_KEY", "defaultsecret")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///database/school.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Environment ---
    FLASK_ENV = os.getenv("FLASK_ENV", "development")

    # --- Email Config ---
    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")

    # --- Twilio SMS Config ---
    TWILIO_SID = os.getenv("TWILIO_SID")
    TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
    TWILIO_FROM = os.getenv("TWILIO_FROM")
