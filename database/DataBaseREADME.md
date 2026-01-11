# 🏙️ CivicEye – Database Schema (README)

CivicEye is a smart city complaint management system where citizens can report infrastructure issues such as **potholes, garbage, and water leakage**.
The platform uses **AI-based detection** and **admin verification** to ensure accurate and fast resolution.

This document explains the **SQLite database schema** used in the CivicEye project.

---

## 📌 Features Supported by Database

- User registration and authentication
- Role-based access (User / Admin)
- Complaint submission with image and address
- AI-based complaint detection
- Admin and AI decision tracking
- Full AI audit history
- Secure and consistent data storage

---

## 🗄️ Database Overview

The database uses a **relational SQLite design** with foreign key constraints enabled.

**Main tables:**
- `users`
- `complaints`
- `ai_detections`

---

## 👤 Users Table

Stores all registered users and administrators.

| Column | Type | Description |
|------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | User name |
| email | TEXT | Unique login email |
| password_hash | TEXT | Hashed password |
| role | TEXT | `admin` or `user` |
| created_at | TIMESTAMP | Account creation time |

---

## 🧾 Complaints Table

Stores all complaints submitted by users.

### Basic Information

| Column | Description |
|------|-------------|
| id | Complaint ID |
| user_id | User who submitted |
| complaint_type | User-provided type |
| image_path | Image file path |
| address | Complaint address |
| description | Complaint details |
| created_at | Submission time |
| updated_at | Last update |

---

### Complaint Status

- pending
- verified
- rejected
- resolved

---

### 🤖 AI & Admin Decision (Latest)

| Column | Description |
|------|-------------|
| ai_result | Full AI output |
| ai_detected_type | AI predicted category |
| ai_confidence | Confidence score |
| ai_status | AI decision |
| decision_source | AI or Admin |
| decision_timestamp | Decision time |
| ai_model_name | AI model used |

---

## 🧠 AI Detections Table (Audit Log)

Stores all AI detections for a complaint.

| Column | Description |
|------|-------------|
| id | Detection ID |
| complaint_id | Related complaint |
| detected_type | AI prediction |
| confidence | Confidence score |
| model_name | AI model |
| created_at | Detection time |

---

## 🔗 Relationships

- One user → many complaints
- One complaint → many AI detections
- Cascade delete enabled

---

## 🔐 Security

- Passwords are hashed
- Role-based access control
- AI and Admin decisions logged

---

## 🚀 Ready for Integration

Compatible with Flask, Django, and AI pipelines.
