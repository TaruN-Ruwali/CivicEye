import os

BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
SQLITE_DB_PATH = os.path.join(BASE_DIR, "database", "civic_eye.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "frontend", "uploads")
SECRET_KEY = os.environ.get("CIVICEYE_SECRET_KEY", "change-this-in-prod")
POTHOLE_MODEL_PATH = os.environ.get("CIVICEYE_POTHOLE_MODEL")
