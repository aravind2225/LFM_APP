# 📊 Log & File Management Platform  
*A Mini SharePoint + Splunk-Style Log Management System*

---

# 🚨 Problem Statement

Organizations generate huge volumes of logs from applications, servers, and cloud services.  
These logs:

- Arrive in multiple formats (TXT, CSV, JSON, XML)
- Are scattered across teams and environments
- Are difficult to search, analyze, and monitor
- Lack centralized security and audit tracking

There is a strong need for a **centralized, secure, and scalable log management system** that enables teams to upload, process, explore, and analyze logs collaboratively.

---

# 🧩 Project Overview

This project is a **Log & File Management Platform** that provides:

- Multi-format log ingestion
- Automatic parsing & categorization
- Advanced log search & filtering
- Real-time analytics dashboards
- Role-based access control
- Complete audit trail
- Automated archive lifecycle

The system is designed as a **mini SharePoint + Splunk hybrid**, enabling secure collaboration and operational visibility.

---

# 🏗️ System Architecture

The application follows a **layered architecture**.


## Frontend Layer
- HTML / CSS
- Jinja Templates (server-side rendering)
- Admin and User dashboards

## Backend Layer (Flask)
- Blueprints / Routes
- Authentication & Authorization
- File Upload Module
- Log Viewing & Dashboard Modules
- Admin Management Modules
- Issue Reporting Module

## Log Processing Pipeline
- User Uploads a File or Multiple files
- That files are stored locally
- Each file processed one by one (If we get multiple files)
    - File's Meta data is stored into raw_files table (along with unique hashkey)
    - Input file object is converted into line by line string if it is text file
    - Input file object is converted into dictionary generator if it is CSV/XML/JSON
        - Then the every log format is normalized to dictionary format (This is the place where log cleaning happens)
        - Now, Based on the message present in that dictionary (Log entry we say), the log is cateogrized
        - And then Log is Inserted into log_entries table
    - This process will repeat for every raw log Entry in the file
- This process will repeat for every log file





Pipeline responsibilities:
- Handle multi-line logs and stack traces
- Extract timestamps, severity, messages
- Categorize logs automatically


## Infrastructure
- Gunicorn WSGI Server
- Render Deployment Platform
- Designed for NGINX Load Balancing

---

# 🗄️ Database Architecture

Database: **PostgreSQL (Supabase Hosted)**

The database is fully normalized and designed for scalability.

## User & Access Management Tables
- users
- user_credentials
- roles
- permissions
- user_roles
- teams
- user_teams

Features:
- Role-based access control (Admin / End User)
- Team-based collaboration
- Account lock after failed logins
- Soft delete users
- Audit triggers

---

## File Management Tables
- raw_files
- file_formats
- log_categories
- log_severities
- environments

Stores:
- File metadata
- Ownership & teams
- File size & upload time
- Archive status

---

## Log Storage
- log_entries

Stores:
- File reference
- Timestamp
- Severity
- Category
- Message content

---

## Audit & Compliance
- audit_trail

Tracks:
- INSERT / UPDATE / DELETE actions
- Acting user
- File name (when applicable)
- Timestamp

Implemented via PostgreSQL triggers.

---

## Archive Lifecycle
- archives

Automatically archives older files.

---

# ⚙️ Major Functionalities

## User & Access Management
- Role-based access (Admin / End User)
- Team-based collaboration
- Secure login and account lockout
- Self account deletion
- Full audit trail

## Multi-Format File Ingestion
- Upload TXT, CSV, JSON, XML
- Multi-file upload support
- Metadata capture (team, environment, size)

## File Processing & Log Parsing
- Parser → Normalizer → Categorizer → Inserter
- Supports multi-line logs and stack traces
- Automatic severity & category detection

## Log Searching & Exploration
- View logs uploaded:
  - By user
  - By team
  - By admins
- Filters:
  - Severity
  - Category
  - Environment
  - File source

## Analytics & Dashboards
- Real-time metrics
- Charts and insights
- Team & user contributions
- Error tracking

## Automation of File Archives
- Automatic archiving of older files
- Lifecycle management

## Reporting of Issues
- Users can report and track issues

---

# 🛠️ Tech Stack

## Frontend
- HTML5
- CSS3
- Jinja2 Templates

## Backend
- Python
- Flask
- Flask-Login
- SQLAlchemy

## Database
- PostgreSQL (Supabase)


## Deployment & Infrastructure
- Render (Cloud Deployment)
- Gunicorn (WSGI Server)

## Tools & Libraries
- psycopg2
- Regex Parsing
- XML / JSON / CSV Parsers
- Git & GitHub

---

# 📈 Scalability & Design Principles

- Modular blueprint architecture
- SQLAlchemy connection pooling
- Database normalization
- Audit-driven security

---

# 🎯 Outcome

A **secure, scalable, and production-ready log management platform** that enables:

- Centralized log collaboration
- Operational monitoring & analytics
- Strong access control & auditing
- Future scalability and performance optimization

---

# 🚀 Future Enhancements

- Async log parsing (Celery + Redis)
- Real-time alert engine
- Advanced search indexing
- Live dashboard updates

---

**Author:** Aravind Udiyana
