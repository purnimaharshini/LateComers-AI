import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ✅ Prefer DATABASE_URL from Render
    _db_url = os.getenv("DATABASE_URL")

    if _db_url:
        # Render sometimes uses "postgres://" — SQLAlchemy needs "postgresql+psycopg2://"
        if _db_url.startswith("postgres://"):
            _db_url = _db_url.replace("postgres://", "postgresql+psycopg2://", 1)
        SQLALCHEMY_DATABASE_URI = _db_url
    else:
        # Local fallback to SQLite (only for development)
        SQLALCHEMY_DATABASE_URI = "sqlite:///database/school.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "defaultsecret")

    # Optional email settings
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USER = os.getenv("MAIL_USER")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    # Twilio keys (optional)
    TWILIO_SID = os.getenv("TWILIO_SID")
    TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
    TWILIO_FROM = os.getenv("TWILIO_FROM")
