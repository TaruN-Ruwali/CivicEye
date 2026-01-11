from typing import Optional, Dict, Any
from werkzeug.security import generate_password_hash, check_password_hash
from backend import model

def register_user(name: Optional[str], email: str, password: str, role: str = "user") -> Dict[str, Any]:
    if model.get_user_by_email(email):
        return {"ok": False, "error": "Email already registered"}
    pw_hash = generate_password_hash(password)
    user_id = model.create_user(name, email, pw_hash, role)
    return {"ok": True, "user_id": user_id}

def login_user(email: str, password: str) -> Dict[str, Any]:
    u = model.get_user_by_email(email)
    if not u:
        return {"ok": False, "error": "Invalid credentials"}
    if not check_password_hash(u["password_hash"], password):
        return {"ok": False, "error": "Invalid credentials"}
    return {"ok": True, "user": {"id": u["id"], "name": u["name"], "email": u["email"], "role": u["role"]}}

def is_admin(user_id: int) -> bool:
    u = model.get_user_by_id(user_id)
    if not u:
        return False
    return u["role"] == "admin"

