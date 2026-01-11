import os
import sqlite3
from typing import Optional, List, Dict, Any
from backend.config import SQLITE_DB_PATH

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(schema_path: Optional[str] = None) -> None:
    path = schema_path or os.path.join(os.path.dirname(os.path.abspath(os.path.join(__file__, ".."))), "database", "schema.sql")
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    conn = get_connection()
    try:
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()

def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    cur = conn.execute(f"PRAGMA table_info({table})")
    cols = [r["name"] for r in cur.fetchall()]
    return column in cols

def migrate_db() -> None:
    """
    Migration-safe upgrades:
    - Add AI decision fields to complaints
    - Create ai_detections table (if not exists)
    - Ensure complaint_type column exists
    """
    conn = get_connection()
    try:
        # Add new columns to complaints if missing
        if not _column_exists(conn, "complaints", "complaint_type"):
            conn.execute("ALTER TABLE complaints ADD COLUMN complaint_type TEXT")
        if not _column_exists(conn, "complaints", "address"):
            conn.execute("ALTER TABLE complaints ADD COLUMN address TEXT")
        if not _column_exists(conn, "complaints", "description"):
            conn.execute("ALTER TABLE complaints ADD COLUMN description TEXT")
        if not _column_exists(conn, "complaints", "ai_result"):
            conn.execute("ALTER TABLE complaints ADD COLUMN ai_result TEXT")
        if not _column_exists(conn, "complaints", "ai_detected_type"):
            conn.execute("ALTER TABLE complaints ADD COLUMN ai_detected_type TEXT")
        if not _column_exists(conn, "complaints", "ai_status"):
            conn.execute("ALTER TABLE complaints ADD COLUMN ai_status TEXT CHECK(ai_status IN ('pending','verified','rejected')) DEFAULT 'pending'")
        if not _column_exists(conn, "complaints", "decision_source"):
            conn.execute("ALTER TABLE complaints ADD COLUMN decision_source TEXT CHECK(decision_source IN ('AI','Admin'))")
        if not _column_exists(conn, "complaints", "decision_timestamp"):
            conn.execute("ALTER TABLE complaints ADD COLUMN decision_timestamp TIMESTAMP")
        if not _column_exists(conn, "complaints", "ai_model_name"):
            conn.execute("ALTER TABLE complaints ADD COLUMN ai_model_name TEXT")
        if not _column_exists(conn, "complaints", "ai_confidence"):
            conn.execute("ALTER TABLE complaints ADD COLUMN ai_confidence REAL")
        if not _column_exists(conn, "complaints", "ai_detected"):
            conn.execute("ALTER TABLE complaints ADD COLUMN ai_detected BOOLEAN DEFAULT 0")
        if not _column_exists(conn, "complaints", "ai_label"):
            conn.execute("ALTER TABLE complaints ADD COLUMN ai_label TEXT")
        if not _column_exists(conn, "complaints", "ai_reviewed_at"):
            conn.execute("ALTER TABLE complaints ADD COLUMN ai_reviewed_at TIMESTAMP")

        # Create ai_detections table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                complaint_id INTEGER NOT NULL,
                detected_type TEXT,
                confidence REAL,
                model_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(complaint_id) REFERENCES complaints(id) ON DELETE CASCADE
            )
            """
        )
        conn.commit()
    finally:
        conn.close()

def create_user(name: Optional[str], email: str, password_hash: str, role: str = "user") -> int:
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, role),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    try:
        cur = conn.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    try:
        cur = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_or_create_anonymous_user() -> int:
    email = "anonymous@civiceye.local"
    u = get_user_by_email(email)
    if u:
        return int(u["id"])
    return create_user("Anonymous", email, "!", "user")

def create_complaint(
    user_id: int,
    image_path: Optional[str],
    description: Optional[str],
    category: Optional[str],
    location: Optional[str],
    status: str = "pending",
    ai_detected: Optional[bool] = None,
    ai_label: Optional[str] = None,
    ai_confidence: Optional[float] = None,
) -> int:
    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO complaints 
               (user_id, image_path, description, category, location, status, 
                ai_detected, ai_label, ai_confidence) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, image_path, description, category, location, status,
             ai_detected, ai_label, ai_confidence),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

def get_user_complaints(user_id: int) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cur = conn.execute(
            "SELECT * FROM complaints WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def get_all_complaints() -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        cur = conn.execute("SELECT * FROM complaints ORDER BY created_at DESC")
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def update_complaint_status(complaint_id: int, status: str) -> bool:
    conn = get_connection()
    try:
        cur = conn.execute(
            "UPDATE complaints SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, complaint_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()

def update_complaint_ai_info(
    complaint_id: int,
    ai_detected: bool,
    ai_label: Optional[str] = None,
    ai_confidence: Optional[float] = None,
) -> bool:
    """
    Update AI detection information for a complaint.
    
    Args:
        complaint_id: ID of the complaint to update
        ai_detected: Whether garbage was detected by AI
        ai_label: Type/label of garbage detected
        ai_confidence: Confidence score (0.0 to 1.0)
        
    Returns:
        True if update was successful, False otherwise
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            """UPDATE complaints 
               SET ai_detected = ?, ai_label = ?, ai_confidence = ?, 
                   updated_at = CURRENT_TIMESTAMP 
               WHERE id = ?""",
            (ai_detected, ai_label, ai_confidence, complaint_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()

def save_ai_detection(
    complaint_id: int,
    detected_type: Optional[str],
    confidence: Optional[float],
    model_name: Optional[str] = None,
    ai_result_text: Optional[str] = None,
) -> None:
    """
    Persist AI detection into ai_detections and update complaints summary fields.
    Sets ai_status to 'pending' for admin review.
    """
    conn = get_connection()
    try:
        # Insert detection record (history)
        conn.execute(
            "INSERT INTO ai_detections (complaint_id, detected_type, confidence, model_name) VALUES (?, ?, ?, ?)",
            (complaint_id, detected_type, confidence, model_name),
        )
        # Update complaints with latest AI decision metadata
        # Set ai_status to 'pending' so admin can review
        conn.execute(
            """
            UPDATE complaints
               SET ai_detected_type = ?,
                   ai_confidence = ?,
                   ai_model_name = ?,
                   ai_status = 'pending',
                   decision_source = 'AI',
                   decision_timestamp = CURRENT_TIMESTAMP,
                   ai_reviewed_at = CURRENT_TIMESTAMP,
                   ai_result = COALESCE(?, ai_result),
                   updated_at = CURRENT_TIMESTAMP
             WHERE id = ?
            """,
            (detected_type, confidence, model_name, ai_result_text, complaint_id),
        )
        conn.commit()
    finally:
        conn.close()

def save_complaint(
    user_id: int,
    image_path: Optional[str],
    address: Optional[str],
    description: Optional[str],
    complaint_type: Optional[str] = None,
) -> int:
    """
    Save a new complaint with image, address, and description.
    This is the main function for registering complaints.
    
    Args:
        user_id: ID of the user submitting the complaint
        image_path: Path to the uploaded image file
        address: Address/location of the complaint
        description: Description of the complaint
        complaint_type: Type of complaint (e.g., "garbage", "pothole")
        
    Returns:
        ID of the created complaint
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO complaints 
               (user_id, complaint_type, image_path, address, description, status, created_at) 
               VALUES (?, ?, ?, ?, ?, 'pending', CURRENT_TIMESTAMP)""",
            (user_id, complaint_type, image_path, address, description),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

def get_complaint_with_ai_result(complaint_id: int) -> Optional[Dict[str, Any]]:
    """
    Return complaint details along with latest AI decision metadata and last detection record.
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            """
            SELECT c.*,
                   (SELECT detected_type FROM ai_detections d WHERE d.complaint_id = c.id ORDER BY d.created_at DESC LIMIT 1) AS last_detected_type,
                   (SELECT confidence FROM ai_detections d WHERE d.complaint_id = c.id ORDER BY d.created_at DESC LIMIT 1) AS last_confidence,
                   (SELECT model_name FROM ai_detections d WHERE d.complaint_id = c.id ORDER BY d.created_at DESC LIMIT 1) AS last_model_name,
                   (SELECT created_at FROM ai_detections d WHERE d.complaint_id = c.id ORDER BY d.created_at DESC LIMIT 1) AS last_detection_at
              FROM complaints c
             WHERE c.id = ?
            """,
            (complaint_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def update_ai_decision(
    complaint_id: int,
    status: str,
    override_type: Optional[str],
    admin_id: int,
) -> bool:
    """
    Admin decision: update ai_status and optionally override detected type.
    """
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE complaints
               SET ai_status = ?,
                   ai_detected_type = COALESCE(?, ai_detected_type),
                   decision_source = 'Admin',
                   decision_timestamp = CURRENT_TIMESTAMP,
                   updated_at = CURRENT_TIMESTAMP
             WHERE id = ?
            """,
            (status, override_type, complaint_id),
        )
        conn.commit()
        return True
    finally:
        conn.close()
def get_complaints_by_user_id(user_id: int) -> List[Dict[str, Any]]:
    """
    Get all complaints for a specific user.
    
    Args:
        user_id: ID of the user
        
    Returns:
        List of complaint dictionaries with all fields
    """
    conn = get_connection()
    try:
        cur = conn.execute(
            """SELECT id, complaint_type, image_path, address, description, 
                      status, created_at, ai_result
               FROM complaints 
               WHERE user_id = ? 
               ORDER BY created_at DESC""",
            (user_id,),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def update_complaint_ai_result(complaint_id: int, ai_result: str, status: Optional[str] = None) -> bool:
    """
    Update AI result and optionally status for a complaint.
    
    Args:
        complaint_id: ID of the complaint
        ai_result: AI detection result as text
        status: Optional status update (e.g., "verified" if confidence > threshold)
        
    Returns:
        True if update was successful
    """
    conn = get_connection()
    try:
        if status:
            cur = conn.execute(
                """UPDATE complaints 
                   SET ai_result = ?, status = ?, updated_at = CURRENT_TIMESTAMP 
                   WHERE id = ?""",
                (ai_result, status, complaint_id),
            )
        else:
            cur = conn.execute(
                """UPDATE complaints 
                   SET ai_result = ?, updated_at = CURRENT_TIMESTAMP 
                   WHERE id = ?""",
                (ai_result, complaint_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
