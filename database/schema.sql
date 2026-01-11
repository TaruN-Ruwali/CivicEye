PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin','user')) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    complaint_type TEXT,
    image_path TEXT,
    address TEXT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT CHECK(status IN ('pending','verified','rejected','resolved')) NOT NULL DEFAULT 'pending',
    ai_result TEXT,
    -- AI decision summary fields (latest decision metadata)
    ai_detected_type TEXT,
    ai_confidence REAL,
    ai_status TEXT CHECK(ai_status IN ('pending','verified','rejected')) DEFAULT 'pending',
    decision_source TEXT CHECK(decision_source IN ('AI','Admin')),
    decision_timestamp TIMESTAMP,
    ai_model_name TEXT,
    -- Legacy fields for backward compatibility
    category TEXT CHECK(category IN ('pothole','garbage','water_leakage','other')) DEFAULT 'other',
    location TEXT,
    ai_detected BOOLEAN DEFAULT 0,
    ai_label TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Historical AI detections table (audit trail and multi-model support)
CREATE TABLE IF NOT EXISTS ai_detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    detected_type TEXT,
    confidence REAL,
    model_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(complaint_id) REFERENCES complaints(id) ON DELETE CASCADE
);
