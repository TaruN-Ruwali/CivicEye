CivicEye – Database Schema

This document describes the database design for CivicEye, a smart city platform that enables citizens to report infrastructure issues such as potholes, garbage, and water leakage. The system integrates AI-based detection and admin verification to ensure efficient and transparent issue resolution.

1. Overview

The database supports:

User authentication and role-based access

Complaint submission with images and locations

AI-based analysis of complaints

Admin and AI decision tracking

Full audit trail of AI detections

A relational SQLite database is used to ensure data integrity, consistency, and scalability.

2. Tables
2.1 Users Table

Stores all registered users and administrators.

Field Name	Data Type	Constraints	Description
id	INTEGER (PK)	AUTOINCREMENT	Unique user ID
name	TEXT	—	User name
email	TEXT	UNIQUE, NOT NULL	Login email
password_hash	TEXT	NOT NULL	Hashed password
role	TEXT	CHECK('admin','user'), DEFAULT 'user'	Access role
created_at	TIMESTAMP	DEFAULT CURRENT_TIMESTAMP	Account creation time

Purpose:
Controls authentication and permissions. Admins can verify or reject complaints; users can submit complaints.

2.2 Complaints Table

Stores all complaints submitted by users along with AI and admin decisions.

Core Complaint Fields
Field Name	Data Type	Description
id	INTEGER (PK)	Complaint ID
user_id	INTEGER (FK)	User who submitted the complaint
complaint_type	TEXT	User-provided complaint type
image_path	TEXT	Uploaded image path
address	TEXT	Physical address
description	TEXT	Complaint description
created_at	TIMESTAMP	Submission time
updated_at	TIMESTAMP	Last update time
Complaint Status Tracking
Field Name	Description
status	Overall complaint state (pending, verified, rejected, resolved)
AI Decision (Latest Result)

These fields store only the most recent AI/Admin decision.

Field Name	Description
ai_result	Raw AI output (text/JSON)
ai_detected_type	AI-predicted category
ai_confidence	Confidence score (0–1)
ai_status	AI decision (pending, verified, rejected)
decision_source	AI or Admin
decision_timestamp	Decision time
ai_model_name	AI model used
Legacy / Compatibility Fields
Field Name	Description
category	Old category system
location	Old location field
ai_detected	Boolean AI flag
ai_label	Old AI label

These fields exist to support older system logic and can be removed later.

2.3 AI Detections Table (Audit Log)

Stores every AI detection attempt, not just the latest one.

Field Name	Data Type	Description
id	INTEGER (PK)	Detection ID
complaint_id	INTEGER (FK)	Related complaint
detected_type	TEXT	Predicted type
confidence	REAL	Confidence score
model_name	TEXT	AI model name
created_at	TIMESTAMP	Detection time

Purpose:

AI decision history

Multi-model comparison

Transparency and debugging

Future model training

3. Controlled Values
Complaint Categories

pothole

garbage

water_leakage

other

Complaint Status

pending

verified

rejected

resolved

AI Status

pending

verified

rejected

4. Relationships

One user → many complaints

One complaint → many AI detections

Deleting a user deletes all complaints

Deleting a complaint deletes all AI detections

All enforced using FOREIGN KEY with CASCADE DELETE.

5. Data Integrity

UNIQUE email enforcement

CHECK constraints on roles, categories, and status

FOREIGN KEY constraints for consistency

Automatic timestamping

Cascading deletes to prevent orphan data

6. Security Considerations

Passwords stored as hashes

Role-based access control

Decision source tracking (AI vs Admin)

Immutable AI audit history

7. Performance Considerations

Indexed foreign keys

Indexed status and timestamps

Normalized structure

Lightweight SQLite design suitable for Flask/Django
