import os
from dotenv import load_dotenv

# Only load locally
if not os.getenv("RENDER"):
    load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")
    db_url = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
        SQLALCHEMY_DATABASE_URI = db_url
        print(f"✅ Using PostgreSQL URL: {db_url}")
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///database/school.db"
        print("⚠ Using local SQLite fallback")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "defaultsecret")
