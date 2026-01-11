import os
import uuid
from typing import Set, Optional
from werkzeug.utils import secure_filename
from backend.config import UPLOAD_FOLDER

ALLOWED_EXTENSIONS: Set[str] = {"png", "jpg", "jpeg", "gif", "mp4"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_dir() -> None:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_upload(file_storage, prefix: Optional[str] = "complaint") -> str:
    ensure_upload_dir()
    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    name = f"{prefix}_{uuid.uuid4().hex}.{ext}"
    fname = secure_filename(name)
    abs_path = os.path.join(UPLOAD_FOLDER, fname)
    file_storage.save(abs_path)
    rel_path = os.path.join("frontend", "uploads", fname)
    return rel_path
