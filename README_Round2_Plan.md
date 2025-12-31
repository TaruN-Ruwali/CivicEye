#  CivicEye – Round-2 Upgrade Strategy

This document describes how CivicEye will evolve in Round-2 of Hack The Winter to move from a working prototype into a smarter and more scalable civic complaint platform.

---

##  Round-2 Objective
Strengthen the backend, introduce real AI-based validation, add analytics, and improve system automation while keeping scope realistic and achievable.

---

##  What Will Be Added in Round-2

| Area | Upgrade |
|------|---------|
| AI Detection | Integrate a real ML model to classify images (pothole / garbage / leakage) instead of simulation |
| Data Accuracy | Add minimum-confidence cutoff so invalid uploads are rejected |
| Location Intelligence | Auto-capture geo-coordinates (browser-based) |
| Multi-Department Routing | Complaints auto-assigned to PWD / Jal Nigam / Nagar Palika based on category |
| Admin Tools | Add analytics charts (pending vs resolved, heat-map if time allows) |
| Security | Basic authentication using token / session-cookie |
| Storage | Move from simple JSON/SQLite to SQLite with structured schema and image storage folder |

---

##  Upgraded Technical Design (Round-2 Vision)
```
Citizen Browser → Web Frontend → Flask Backend
↓ ↓
Upload Image Submit Details
↓
AI Classification Model (MobileNet-V2 / YOLO-nano)
↓
Category + Confidence Score
↓
SQLite Database → Admin Dashboard → Status View
```

---




##  AI Model Plan
| Component | Description |
|----------|-------------|
| Dataset | Small custom dataset (~300–600 images) + augmentations |
| Model | Lightweight classifier (MobileNet-V2 or YOLO-nano) |
| Inference | Python + OpenCV + TensorFlow Lite |
| Output | `{type: pothole/garbage/water, confidence: %, valid: true/false}` |

---

##  Backend Enhancements
| Planned Functionality | Notes |
|----------------------|--------|
| Routing Engine | Auto-assign to department using rule-based logic |
| Rate-limit / validation | Prevent spam & duplicate submissions |
| DB Schema | Table structure for complaints, users, departments |

---

## Admin Dashboard – Round-2 Enhancements
| Feature | Description |
|---------|-------------|
| Complaint analytics | Pie chart: Pending / In-Progress / Resolved |
| Filter & search | By location or category |
| Auto-refresh | Dashboard shows latest complaints without reload |
| Department panel | Optional – per-team view |

---

##  Team Work Allocation
| Member | Role |
|--------|------|
| Tarun | Frontend improvements + map/location + admin dashboard charts |
| Jay | AI dataset preparation + model training + inference code |
| Ankush | Backend Flask APIs, DB schema, routing logic |
| Ujjwal | UI polishing, forms validation, documentation, demo prep |

---

##  Deliverables Expected in Round-2
✔ AI classification implemented  
✔ Admin analytics dashboard  
✔ Location auto-capture & stored in DB  
✔ Department routing logic  
✔ Improved security + basic token/session  
✔ Updated README + diagrams + live demo video  

---
