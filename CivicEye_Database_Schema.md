# CivicEye – Database Schema

This document describes the database design for **CivicEye**, a civic grievance reporting system with **basic AI assistance**.  
The AI component is minimal and only supports **optional classification suggestions** at a later stage.

---

## 1. Overview

The database stores:
- User-submitted complaints
- Complaint categories (user-selected or system-suggested)
- Complaint status tracking
- Administrative updates

A **relational database** is used for simplicity, reliability, and easy integration with lightweight AI modules if required.

---

## 2. Tables

### 2.1 Complaints Table

Stores all grievance complaints submitted by users.

| Field Name   | Data Type    | Description |
|-------------|-------------|-------------|
| id          | INTEGER (PK)| Unique complaint ID |
| image_path  | TEXT        | Path to uploaded image |
| description | TEXT        | Complaint description |
| category    | TEXT        | Complaint category (may be auto-suggested) |
| status      | TEXT        | Current complaint status |
| location    | TEXT        | Location provided by user |
| created_at  | TIMESTAMP   | Complaint submission time |
| updated_at  | TIMESTAMP   | Last update time |

---

## 2.2 Category Values (Controlled)

- pothole  
- garbage  
- water_leakage  
- other  

These categories can later be **assisted by an AI model**, but final control remains with authorities.

---

## 2.3 Status Values (Controlled)

- Submitted  
- Verified  
- In Progress  
- Resolved  
- Rejected  

This ensures structured and traceable complaint handling.

---

## 3. SQL Table Definition (Stage-1)

```sql
CREATE TABLE complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_path TEXT NOT NULL,
    description TEXT,
    category TEXT CHECK(category IN ('pothole', 'garbage', 'water_leakage', 'other')),
    status TEXT CHECK(status IN ('Submitted', 'Verified', 'In Progress', 'Resolved', 'Rejected'))
           DEFAULT 'Submitted',
    location TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
