#  CivicEye – Smart Civic Issue Reporting Platform

CivicEye is a web-based civic infrastructure reporting system that empowers citizens to submit road defects (potholes, garbage, leakage etc.) and enables authorities to track, verify, and resolve them efficiently.

This prototype demonstrates:

 Citizen portal (Submit complaints + View status)  
 Admin portal (Manage complaints + Update resolution stage)  
 Data persistence using SQLite  
 Simulated AI validation pipeline (Round-2 upgrade planned)

---

##  Problem Statement
Cities struggle with delayed civic maintenance because:
- Citizens have no direct digital way to report issues
- Complaints get lost due to manual processes
- Authorities lack real-time dashboards to track field issues

CivicEye bridges this gap by digitally connecting **citizens ↔ municipalities** through a smart reporting platform.

---

##  Core Features (Prototype – Round-1)
| Feature | Citizen Web | Admin Panel |
|--------|-------------|-------------|
| Login / Register | ✅ |  Private |
| Submit complaint (image + details) | ✅ | — |
| View complaint status | ✅ | — |
| Dashboard showing all complaints | — | ✅ |
| Change status (Pending → In-Progress → Resolved) | — | ✅ |
| Persistent storage (SQLite) |  Automatic |  Automatic |
| AI Validation (simulated score) |  Planned |  Planned |

---

##  Architecture Overview


 Full architecture diagram and all other diagrams are included in the folder `/Diagrams`

---

##  Tech Stack
**Frontend** – HTML, CSS, JavaScript  
**Backend** – Python Flask REST API  
**Database** – SQLite  
**AI Layer** – Placeholder simulation (to be replaced with ML model in Round-2)  

---

##  Repository Structure
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

##  Installation & Setup (Prototype)

### 1️ Install Dependencies
```bash
pip install flask flask-cors
```
### 2️ Run Server
```bash
 python -m flask --app backend.server run --debug
```
### 3️ Open HTML files
```bash
frontend/index.html  → Citizen Login

frontend/admin.html  → Admin Dashboard
```

---

##  Team "iPad Chor" – GEHU Bhimtal

| Name         | Role                 |
| ------------ | -------------------- |
| Tarun Ruwali | Frontend Web Dev     |
| Jay Negi     | AI / ML              |
| Ankush   Rawat    | Backend & Database   |
| Ujjwal  Bhatt     | Tester / UI Details  |

---

##  Why CivicEye is Impactful

 Reduces complaint delay → faster civic repairs

 Improves transparency between public & government

 Gives real-time actionable dashboard to authorities

 AI keeps false complaints out → higher efficiency
