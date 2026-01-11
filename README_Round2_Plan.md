#  CivicEye – Round-2 Development Plan

**CivicEye** is a civic issue reporting platform that allows citizens to upload photos of infrastructure problems (like potholes and leaks) and track their status. The Round-1 prototype demonstrated a working frontend (HTML, CSS, JS) and a basic admin panel. In Round-2, our focus is on improving the **technical foundation**, adding **real data processing**, and moving from prototype logic toward a **more complete system design** that still stays within our development capacity.

---

##  What We Have Today

In Round-1 we built:

 User login and registration pages (`index.html`, `register.html`)  
 Complaint submission page with image upload (`submit.html`)  
 Status tracking page showing complaint list (`status.html`)  
 Admin panel to view and update complaints (`admin.html`)  
 Basic routing based on user role  
 Static frontend pages connected with basic JS logic  
 A clear folder structure

These files and interactions form the current prototype:

```
CivicEye/
│
|── Diagrams/
│ ├── Admin-Complaint-Management-Flow.png
│ ├── System-Architecture.png
│ ├── User-Flow-Diagram.png
|
├── Screenshots/
│ ├── Admin-Portal.png
│ ├── Complain-Page.png
│ ├── Login-Page.png
│ ├── Register-Page.png
│ └── Status-Pages.png
|
├── backend/
│ ├── ai_engine.py
│ ├── app.py
│ ├── model.py
│ ├── requirements.txt
│ ├── server.py
│ └── utils.py
│
├── database/
| |── CivicEye_Database_schema.md
│ ├── ER Diagram.png
│ ├── civic_eye.db
│ └── schema.sql
|
├── .gitignore
├── README.md
├── README_Flow.md
└── README_Round2_Plan.md
```


---

##  Round-2 Focus Areas

For this round, we are targeting improvements in the following areas:

###  1. Real Image Validation Logic
- Replace the current **simulation placeholder** with a simple trained model.
- We will use a small dataset and a lightweight model (like MobileNetv2) to distinguish:
  - Valid complaints (e.g., potholes, trash, leaks)
  - Invalid or unrelated images
- This model will run server-side in Python, returning:
```{ "label": "pothole", "confidence": 0.78 }```

---

###  2. Backend Improvements

We will continue building in **Flask** with a clearer API design:

| API | Purpose |
|-----|----------|
| `POST /api/auth/login` | Authenticate user |
| `POST /api/auth/register` | Register new user |
| `POST /api/complaints` | Accept complaint + image |
| `GET /api/complaints/user` | List complaints for a user |
| `GET /api/complaints/all` | Admin list of all complaints |
| `PUT /api/complaints/:id` | Admin update status |

These will be implemented in `backend/server.py` and helper modules.

---

##  Technical Enhancements (Depth & Scalability)

Although this is still a prototype, we will:

### Backend
- Improve backend file structure (`/backend/routes.py`, `/backend/models.py`, etc.)
- Add **error handling** for:
- invalid uploads
- missing fields
- unexpected input

### Database
- Enhance **SQLite schema** to support:
- user table
- complaint table with status history
- location (latitude, longitude)
- timestamps (created_at, updated_at)

Example SQL schema:
```sql
CREATE TABLE users (
id INTEGER PRIMARY KEY,
name TEXT,
email TEXT UNIQUE,
password TEXT
);

CREATE TABLE complaints (
id INTEGER PRIMARY KEY,
user_id INTEGER,
image_path TEXT,
description TEXT,
status TEXT,
latitude REAL,
longitude REAL,
created_at TEXT,
updated_at TEXT
);
```
---

### System Architecture
![System Architecture](Diagrams/System-Architecture.png)

---

### Admin Complaint Management Flow
![Flow-Chart](Diagrams/Admin-Complaint-Management-Flow.png)

---

### User Flow Diagram
![User-Flow-Diagram](Diagrams/User-Flow-Diagram.png)

---

### Screenshot
##### Login Page
![User-Flow-Diagram](Screenshots/Login-Page.png)

##### Register Page

![User-Flow-Diagram](Screenshots/Register-Page.png)

##### Complain Page

![User-Flow-Diagram](Screenshots/Complain-Page.png)

##### Status Page

![User-Flow-Diagram](Screenshots/Status-Pages.png)

##### Admin Portal

![User-Flow-Diagram](Screenshots/Admin-Portal.png)

---
