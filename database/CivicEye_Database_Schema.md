# CivicEye – Database Schema

This document describes the database design for **CivicEye**, a smart city platform that enables citizens to report infrastructure defects like potholes and cracks. The system connects citizens directly with Public Works Department authorities for efficient issue resolution.

---

## 1. Overview

The database stores:
- User accounts and authentication data
- Infrastructure complaint reports with images and locations
- Complaint status tracking and updates
- Role-based access for users and administrators

A **relational database** is used for data integrity, consistency, and efficient querying of complaint data.

---

## 2. Tables

### 2.1 Users Table

Stores user account information including authentication details and roles.

| Field Name      | Data Type     | Constraints                  | Description |
|-----------------|---------------|------------------------------|-------------|
| id              | INTEGER (PK)  | AUTOINCREMENT              | Unique user ID |
| name            | TEXT          |                              | User's display name (optional) |
| email           | TEXT          | UNIQUE, NOT NULL            | User's email address (login) |
| password_hash   | TEXT          | NOT NULL                   | Hashed password for authentication |
| role            | TEXT          | CHECK(role IN ('admin', 'user')), DEFAULT 'user' | User role for access control (admin or user) |
| created_at      | TIMESTAMP     | DEFAULT CURRENT_TIMESTAMP  | Account creation timestamp |

The Users table manages all registered users of the system. Each user has a unique email that serves as their login credential. The role field determines what actions a user can perform within the system - regular users can submit complaints while admins can manage all complaints.

### 2.2 Complaints Table

Stores all infrastructure complaint reports submitted by users.

| Field Name      | Data Type     | Constraints                  | Description |
|-----------------|---------------|------------------------------|-------------|
| id              | INTEGER (PK)  | AUTOINCREMENT              | Unique complaint ID |
| user_id         | INTEGER (FK)  | NOT NULL, FOREIGN KEY(users.id) | ID of the user who submitted the complaint |
| image_path      | TEXT          |                              | Path to uploaded image (optional) |
| description     | TEXT          |                              | Complaint description (optional) |
| category        | TEXT          | CHECK(category IN ('pothole', 'garbage', 'water_leakage', 'other')), DEFAULT 'other' | Category of the complaint |
| status          | TEXT          | CHECK(status IN ('pending', 'in_progress', 'resolved')), NOT NULL, DEFAULT 'pending' | Current complaint status |
| location        | TEXT          |                              | Location provided by user |
| created_at      | TIMESTAMP     | DEFAULT CURRENT_TIMESTAMP  | Complaint submission timestamp |
| updated_at      | TIMESTAMP     | DEFAULT CURRENT_TIMESTAMP  | Last status update timestamp |

The Complaints table is the core of the system, storing all infrastructure issues reported by citizens. Each complaint is linked to a user via the user_id foreign key. The table includes fields for optional image uploads, descriptions, and location data to help authorities identify and address the reported issues. The status field tracks the progress of each complaint from submission to resolution.

---

## 2.3 Category Values (Controlled)

- pothole  
- garbage  
- water_leakage  
- other  

Categories are used to classify different types of infrastructure issues for better organization and tracking. The system enforces these specific categories to maintain consistency in how complaints are categorized.

---

## 2.4 Status Values (Controlled)

- pending      (Complaint submitted, awaiting review)
- in_progress  (Work has started on the issue)
- resolved     (Issue has been fixed)

The status values provide a clear workflow for managing complaints. When a complaint is first submitted, it enters the 'pending' state. As work begins on addressing the issue, it moves to 'in_progress', and finally to 'resolved' when the problem has been fixed.

---

## 2.5 Indexes

- idx_complaints_user_id: Index on user_id for efficient user complaint queries
- idx_complaints_status: Index on status for efficient status-based queries
- idx_complaints_created_at: Index on created_at for efficient time-based queries

Database indexes are implemented to optimize common query patterns. The user_id index allows for quick retrieval of all complaints by a specific user. The status index enables efficient filtering of complaints by their current status. The created_at index supports chronological ordering and time-based filtering of complaints.

---

## 3. Relationships

The database implements a one-to-many relationship between Users and Complaints. Each user can submit multiple complaints, but each complaint is associated with exactly one user. The foreign key constraint ensures referential integrity - if a user account is deleted, all associated complaints are also removed from the system.

---

## 4. Data Integrity

The database schema includes several constraints to maintain data quality:

- UNIQUE constraint on user email addresses to prevent duplicate accounts
- NOT NULL constraints on required fields to ensure essential information is always captured
- CHECK constraints on category and status fields to enforce valid values
- FOREIGN KEY constraint to maintain referential integrity between users and complaints
- CASCADE delete rule to automatically remove related complaints when a user is deleted

---

## 5. Security Considerations

- Passwords are stored as hashed values, not in plain text
- User roles control access to different system functions
- Email addresses serve as unique identifiers for user accounts
- Timestamps track when records are created and modified

---

## 6. Performance Considerations

- Indexes on frequently queried columns improve query performance
- Proper normalization reduces data redundancy
- Timestamps enable efficient time-based queries and reporting
- Foreign key constraints maintain data consistency

