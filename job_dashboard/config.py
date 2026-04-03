import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32).hex())
    SQLALCHEMY_DATABASE_URI = "sqlite:///job_dashboard.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {"pdf", "docx", "doc", "txt"}

    # Adzuna API
    ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID", "")
    ADZUNA_API_KEY = os.environ.get("ADZUNA_API_KEY", "")
    ADZUNA_COUNTRY = os.environ.get("ADZUNA_COUNTRY", "us")

    # RapidAPI / JSearch
    RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "")

    WTF_CSRF_ENABLED = True
