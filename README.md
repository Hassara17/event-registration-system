# Event Registration System

A full-stack **Event Registration System** for managing events, sessions, attendees, registrations, staff assignments, check-ins, dashboards, capacity monitoring, and registration history.

The system is built with a **FastAPI backend**, **PostgreSQL database**, **Alembic migrations**, and a **React + Vite frontend**.

---

## Table of Contents

* [Overview](#overview)
* [Features](#features)
* [User Roles](#user-roles)
* [Registration Lifecycle](#registration-lifecycle)
* [Technology Stack](#technology-stack)
* [System Architecture](#system-architecture)
* [Project Structure](#project-structure)
* [Database](#database)
* [Backend API](#backend-api)
* [Getting Started](#getting-started)
* [Environment Configuration](#environment-configuration)
* [Database Setup](#database-setup)
* [Creating Demo Users](#creating-demo-users)
* [Running the Backend](#running-the-backend)
* [Running the Frontend](#running-the-frontend)
* [Authentication](#authentication)
* [Role-Based Access Control](#role-based-access-control)
* [Event Management](#event-management)
* [Session Management](#session-management)
* [Registration Management](#registration-management)
* [Staff Assignment](#staff-assignment)
* [Check-In](#check-in)
* [Search, Filtering and Pagination](#search-filtering-and-pagination)
* [CSV Import and Export](#csv-import-and-export)
* [Dashboard and Statistics](#dashboard-and-statistics)
* [Capacity Alerts](#capacity-alerts)
* [Registration History](#registration-history)
* [Security](#security)
* [Error Handling](#error-handling)
* [API Documentation](#api-documentation)
* [Testing Checklist](#testing-checklist)
* [Development Decisions](#development-decisions)
* [Future Improvements](#future-improvements)
* [Project Status](#project-status)
* [License](#license)

---

# Overview

The Event Registration System provides a centralized platform for organizing events and managing participant registrations.

The system supports three primary user roles:

* **Attendee**
* **Organizer**
* **Check-in Staff**

Each role has different permissions and responsibilities.

The application manages the complete registration lifecycle, from event discovery and registration to confirmation, cancellation, expiration, and check-in.

---

# Features

## Authentication

* User registration
* User login
* Password hashing
* JWT-based authentication
* Current-user endpoint
* Role-based authorization
* Protected API endpoints

## Event Management

Organizers can:

* Create events
* Edit events
* Archive events
* Restore archived events
* View events
* Manage event details

## Session Management

Organizers can:

* Create sessions
* Edit sessions
* Delete sessions
* Set session capacity
* Define session start time
* Define session duration
* Set session location

## Registration Management

Attendees can:

* Browse events
* View sessions
* Register for sessions
* View their registrations
* Cancel eligible registrations
* View registration history

Organizers and authorized staff can:

* View registrations
* Confirm registrations
* Cancel registrations
* Manage registration status
* Check attendees in

## Staff Management

Organizers can:

* Assign check-in staff to sessions
* View assigned staff
* Manage session staff assignments

Check-in staff can:

* View assigned sessions
* View registrations for assigned sessions
* Perform check-in operations

## Dashboard

The system provides dashboard information such as:

* Total events
* Total sessions
* Registration statistics
* Confirmed registrations
* Checked-in attendees
* Capacity information

## Capacity Monitoring

The system tracks session capacity and registration usage.

Capacity counts include:

* Reserved
* Confirmed
* Checked In

The system can also provide capacity-related alerts.

## Search and Filtering

Supported functionality includes:

* Event search
* Session filtering
* Registration filtering
* Status filtering
* Pagination

## CSV Import and Export

The system supports CSV-based operations for registration-related data.

---

# User Roles

## Attendee

Attendees can:

* Register for an account
* Log in
* Browse events
* View sessions
* Register for sessions
* View their registrations
* Cancel eligible registrations
* View registration history
* Manage their profile

Attendees cannot:

* Create events
* Create sessions
* Change session capacity
* Assign staff
* Perform staff-level check-in operations

---

## Organizer

Organizers have administrative capabilities for event management.

They can:

* Create events
* Edit events
* Archive events
* Restore events
* Create sessions
* Edit sessions
* Delete sessions
* Change capacity
* View registrations
* Manage registrations
* Assign check-in staff
* View dashboards
* View statistics
* View capacity alerts
* Import/export CSV data

---

## Check-in Staff

Check-in staff have operational permissions for sessions assigned to them.

They can:

* View assigned sessions
* View registrations for assigned sessions
* Confirm eligible registrations
* Cancel eligible registrations
* Check attendees in

They cannot:

* Create events
* Create sessions
* Change session capacity
* Assign staff
* Perform organizer-level administrative operations

---

# Registration Lifecycle

A registration follows a controlled lifecycle.

```text
Reserved
   │
   ├──> Confirmed
   │       │
   │       └──> Checked In
   │
   ├──> Cancelled
   │
   └──> Expired
```

## Registration States

| Status     | Description                                            |
| ---------- | ------------------------------------------------------ |
| Reserved   | Registration has been created but is not yet confirmed |
| Confirmed  | Registration has been successfully confirmed           |
| Checked In | Attendee has checked in                                |
| Cancelled  | Registration has been cancelled                        |
| Expired    | Registration has expired                               |

Registration history is preserved so that previous state changes are not lost.

---

# Technology Stack

## Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* Alembic
* PostgreSQL
* Uvicorn
* JWT Authentication
* Password hashing

## Frontend

* React
* Vite
* JavaScript
* HTML
* CSS

## Development Tools

* Git
* GitHub
* REST API
* Swagger/OpenAPI
* PostgreSQL
* Python Virtual Environment

---

# System Architecture

```text
                    ┌──────────────────────┐
                    │     React Frontend   │
                    │      Vite + React    │
                    └──────────┬───────────┘
                               │
                               │ HTTP / REST API
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    │                      │
                    │ Authentication       │
                    │ Authorization        │
                    │ Events               │
                    │ Sessions             │
                    │ Registrations        │
                    │ Staff Management     │
                    │ Check-in             │
                    │ Dashboard            │
                    └──────────┬───────────┘
                               │
                               │ SQLAlchemy
                               ▼
                    ┌──────────────────────┐
                    │      PostgreSQL      │
                    │       Database       │
                    └──────────────────────┘
```

---

# Project Structure

```text
event-registration-system/
│
├── backend/
│   │
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── seed.py
│   │   └── main.py
│   │
│   ├── alembic/
│   │   └── versions/
│   │
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   │
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── routes/
│   │   └── App.jsx
│   │
│   ├── package.json
│   └── vite.config.js
│
├── README.md
└── .gitignore
```

---

# Database

The application uses **PostgreSQL** as the primary database.

The database stores information related to:

* Users
* Events
* Sessions
* Registrations
* Session staff
* Registration history

Database schema changes are managed using **Alembic migrations**.

---

# Backend API

The backend exposes REST APIs for the application's major operations.

Main API areas include:

```text
/auth
/events
/sessions
/registrations
/users
/staff
/dashboard
/capacity-alerts
```

Examples:

```text
POST   /auth/register
POST   /auth/login
GET    /auth/me

GET    /events
POST   /events

GET    /sessions
POST   /sessions

GET    /registrations
POST   /registrations

POST   /registrations/{id}/confirm
POST   /registrations/{id}/cancel
POST   /registrations/{id}/check-in
```

The exact available endpoints can be viewed through the automatically generated API documentation.

---

# Getting Started

## Prerequisites

Install the following software before running the project:

* Python 3.10+
* Node.js
* npm
* PostgreSQL
* Git

Verify the installations:

```bash
python --version
node --version
npm --version
psql --version
git --version
```

---

# Clone the Repository

```bash
git clone https://github.com/Hassara17/event-registration-system.git
```

Navigate into the project:

```bash
cd event-registration-system
```

---

# Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a Python virtual environment:

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Environment Configuration

Create a `.env` file inside the `backend` directory.

Example:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/event_registration
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Replace:

```text
your_password
```

with your PostgreSQL password.

Use a strong secret key for `SECRET_KEY`.

---

# Database Setup

Create the PostgreSQL database:

```sql
CREATE DATABASE event_registration;
```

Then make sure the database configuration in `.env` points to this database.

From the `backend` directory, run the migrations:

```bash
alembic upgrade head
```

This creates the required database tables.

---

# Creating Demo Users

The application supports three user roles:

```text
attendee
organizer
checkin_staff
```

## Attendee

Attendees can be created through the application's public registration endpoint.

A newly registered user is automatically assigned the:

```text
attendee
```

role.

You can create an attendee through the frontend registration page or the API:

```text
POST /auth/register
```

---

## Organizer and Check-in Staff

Organizer and Check-in Staff accounts are created using the seed script:

```text
backend/app/seed.py
```

### Run the Seed Script

Make sure your terminal is inside the `backend` directory:

```bash
cd backend
```

Then run:

```bash
python app/seed.py
```

The seed script creates the demo Organizer and Check-in Staff accounts if they do not already exist.

The seed operation is designed to avoid creating duplicate users when the demo accounts already exist.

---

## Demo Credentials

| Role           | Name                | Email                   | Password        |
| -------------- | ------------------- | ----------------------- | --------------- |
| Organizer      | Demo Organizer      | `organizer@example.com` | `Organizer@123` |
| Check-in Staff | Demo Check-in Staff | `staff@example.com`     | `Staff@123`     |

For an attendee account, use the normal registration page/API to create an account.

> **Important:** These are demo credentials intended for local development/testing. Do not use them in a production deployment.

---

# Recommended Setup Order

For a fresh installation, follow this order:

```text
1. Clone repository
2. Configure PostgreSQL
3. Create event_registration database
4. Configure backend .env
5. Create Python virtual environment
6. Install backend dependencies
7. Run Alembic migrations
8. Run backend/app/seed.py
9. Start FastAPI backend
10. Install frontend dependencies
11. Start React frontend
```

---

# Running the Backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

The backend will normally be available at:

```text
http://127.0.0.1:8000
```

---

# Running the Frontend

Open another terminal and navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Vite will display the frontend URL in the terminal, normally:

```text
http://localhost:5173
```

---

# Authentication

Authentication uses JWT-based authentication.

The general authentication flow is:

```text
User
 │
 ├── Register
 │
 └── Login
       │
       ▼
   FastAPI Backend
       │
       ▼
   Validate Credentials
       │
       ▼
   Generate JWT
       │
       ▼
   React Frontend
       │
       ▼
Authenticated Requests
```

Protected API requests include the JWT access token.

The backend validates the token before allowing access to protected resources.

---

# Role-Based Access Control

Authorization is enforced on the backend.

A user's role determines which operations they are allowed to perform.

```text
                    User
                     │
              ┌──────┴──────┐
              │             │
          Authenticated?    │
              │             │
             Yes            │
              │             │
         Check Role         │
              │             │
      ┌───────┼────────┐    │
      │       │        │    │
  Attendee Organizer Staff  │
      │       │        │
      ▼       ▼        ▼    │
  Allowed   Allowed   Allowed
  Actions   Actions   Actions
```

Frontend role restrictions improve the user experience, but the backend remains responsible for enforcing authorization.

---

# Event Management

Organizers can create and manage events.

Typical event information includes:

* Event title
* Description
* Event details
* Event status
* Sessions associated with the event

Organizers can also archive and restore events.

---

# Session Management

Each event can contain multiple sessions.

A session may contain:

* Session title
* Start time
* Duration
* Location
* Capacity
* Event association

Organizers can create, update, and delete sessions.

Capacity is enforced by the backend.

---

# Registration Management

The registration process allows attendees to register for available sessions.

A typical flow is:

```text
Browse Event
     │
     ▼
Select Session
     │
     ▼
Register
     │
     ▼
Reserved
     │
     ▼
Confirm
     │
     ▼
Confirmed
     │
     ▼
Check In
     │
     ▼
Checked In
```

Registrations can also transition to:

```text
Cancelled
Expired
```

depending on the applicable business rules.

---

# Staff Assignment

Organizers can assign check-in staff to sessions.

The relationship is maintained through the session-staff assignment.

```text
Organizer
    │
    ▼
Select Session
    │
    ▼
Assign Check-in Staff
    │
    ▼
Staff can access assigned session
```

Check-in staff should only have access to the sessions assigned to them.

---

# Check-In

Check-in staff can check registered attendees into their assigned sessions.

A typical check-in flow is:

```text
Confirmed Registration
          │
          ▼
    Check-in Staff
          │
          ▼
      Check In
          │
          ▼
      Checked In
```

The backend verifies that the staff member has the required permissions before allowing the operation.

---

# Search, Filtering and Pagination

The application supports data discovery through:

* Search
* Filtering
* Pagination

These capabilities help users efficiently work with larger event and registration datasets.

Examples include:

* Searching events
* Filtering sessions
* Filtering registrations by status
* Paginating registration results

---

# CSV Import and Export

The system supports CSV-based data operations.

CSV functionality can be used to:

* Import registration-related data
* Export registration-related information
* Work with larger datasets

Validation is performed during import to prevent invalid data from being inserted into the database.

---

# Dashboard and Statistics

The dashboard provides an overview of the system.

Depending on the user's role, dashboard information may include:

* Total events
* Total sessions
* Total registrations
* Confirmed registrations
* Cancelled registrations
* Checked-in attendees
* Session capacity
* Registration statistics

Role-specific authorization prevents users from accessing information they are not permitted to view.

---

# Capacity Alerts

The system monitors session capacity.

The capacity calculation considers active registrations:

```text
Reserved
Confirmed
Checked In
```

Example:

```text
Capacity = 100

Reserved     = 20
Confirmed    = 60
Checked In   = 10
------------------
Active       = 90
```

Remaining capacity:

```text
100 - 90 = 10
```

Capacity alerts can be used to identify sessions approaching or reaching their limits.

---

# Registration History

Registration history is maintained separately from the current registration state.

This allows the system to preserve important lifecycle information.

Example:

```text
Reserved
   │
   ▼
Confirmed
   │
   ▼
Checked In
```

The historical states are preserved rather than simply overwriting the previous state.

This provides better traceability and auditing.

---

# Security

The application includes several security mechanisms.

## Password Hashing

Passwords are not stored as plain text.

Passwords are securely hashed before being stored in the database.

## JWT Authentication

Protected endpoints require a valid authentication token.

## Role-Based Authorization

API operations are protected according to the user's role.

## Backend Authorization

Authorization is enforced on the backend rather than relying only on frontend restrictions.

## Input Validation

FastAPI/Pydantic validation is used to validate incoming request data.

## Database Constraints

Database constraints help maintain data integrity.

## Protected Operations

Sensitive operations such as:

* Creating events
* Changing capacity
* Assigning staff
* Checking in attendees

are protected by authorization rules.

---

# Error Handling

The backend uses appropriate HTTP status codes and structured error responses.

Examples include:

| Status Code | Meaning                         |
| ----------- | ------------------------------- |
| `200`       | Successful request              |
| `201`       | Resource created                |
| `400`       | Invalid request                 |
| `401`       | Authentication required/invalid |
| `403`       | Insufficient permissions        |
| `404`       | Resource not found              |
| `409`       | Conflict                        |
| `422`       | Validation error                |
| `500`       | Internal server error           |

Example:

```text
403 Forbidden
```

means that the authenticated user does not have sufficient permission to perform the requested operation.

---

# API Documentation

FastAPI automatically generates interactive API documentation.

After starting the backend, open:

```text
http://127.0.0.1:8000/docs
```

The Swagger UI can be used to:

* View endpoints
* View request schemas
* View response schemas
* Authenticate
* Send test requests
* Inspect API responses

Alternative OpenAPI documentation is available at:

```text
http://127.0.0.1:8000/redoc
```

---

# Testing Checklist

## Authentication

* [ ] Register attendee
* [ ] Login with valid credentials
* [ ] Reject invalid credentials
* [ ] Verify JWT authentication
* [ ] Verify `/auth/me`
* [ ] Verify role information

## Attendee

* [ ] View events
* [ ] View sessions
* [ ] Register for a session
* [ ] View registrations
* [ ] Cancel eligible registration
* [ ] View registration history

## Organizer

* [ ] Create event
* [ ] Edit event
* [ ] Archive event
* [ ] Restore event
* [ ] Create session
* [ ] Edit session
* [ ] Delete session
* [ ] Change capacity
* [ ] View registrations
* [ ] Assign staff
* [ ] View dashboard
* [ ] View capacity alerts
* [ ] Import CSV
* [ ] Export CSV

## Check-in Staff

* [ ] Login as check-in staff
* [ ] View assigned sessions
* [ ] View assigned registrations
* [ ] Confirm registration
* [ ] Cancel eligible registration
* [ ] Check attendee in
* [ ] Verify unauthorized organizer operations are blocked

## Authorization

* [ ] Attendee cannot access organizer operations
* [ ] Attendee cannot assign staff
* [ ] Staff cannot create events
* [ ] Staff cannot modify session capacity
* [ ] Staff cannot assign other staff
* [ ] Staff cannot access unassigned sessions
* [ ] Unauthorized API requests return appropriate errors

## Capacity

* [ ] Registration cannot exceed capacity
* [ ] Reserved registrations count toward capacity
* [ ] Confirmed registrations count toward capacity
* [ ] Checked-in registrations count toward capacity
* [ ] Capacity alerts work correctly

---

# Development Decisions

## FastAPI

FastAPI was selected because it provides:

* High performance
* Automatic OpenAPI documentation
* Pydantic validation
* Easy API development
* Async support

## PostgreSQL

PostgreSQL provides:

* Relational data modeling
* Transaction support
* Strong consistency
* Data integrity
* Production-ready database functionality

## Alembic

Alembic is used to manage database schema migrations.

This allows database changes to be tracked and reproduced across environments.

## React + Vite

React provides component-based frontend development while Vite provides a fast development environment.

## Backend Authorization

Authorization is enforced at the API level so that users cannot bypass security restrictions simply by modifying frontend code.

---

# Development Workflow

A typical development workflow is:

```text
Create/modify feature
        │
        ▼
Update backend/frontend
        │
        ▼
Update database models if required
        │
        ▼
Create Alembic migration
        │
        ▼
Run migration
        │
        ▼
Test API
        │
        ▼
Test frontend
        │
        ▼
Test authorization
        │
        ▼
Commit changes
```

---

# Git Workflow

Check repository status:

```bash
git status
```

Add changes:

```bash
git add .
```

Create a commit:

```bash
git commit -m "Update README"
```

Push changes:

```bash
git push origin master
```

If your current branch is different, replace `master` with the appropriate branch name.

---

# Troubleshooting

## Backend Does Not Start

Check that:

* Python is installed
* Virtual environment is activated
* Dependencies are installed
* PostgreSQL is running
* `.env` is configured correctly
* Database exists
* Alembic migrations have been applied

Run:

```bash
alembic upgrade head
```

---

## Database Connection Error

Verify:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/event_registration
```

Make sure:

* PostgreSQL is running
* Database name is correct
* Username is correct
* Password is correct
* PostgreSQL port is correct

---

## Frontend Does Not Start

Navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Then:

```bash
npm run dev
```

---

## Demo Organizer or Staff User Does Not Exist

Run the seed script from the `backend` directory:

```bash
python app/seed.py
```

Then use:

```text
Organizer
Email: organizer@example.com
Password: Organizer@123
```

or:

```text
Check-in Staff
Email: staff@example.com
Password: Staff@123
```

---

## 403 Forbidden

A `403 Forbidden` response generally means the authenticated user does not have permission to perform the requested operation.

Check:

1. The logged-in user's role.
2. Whether the endpoint requires organizer permissions.
3. Whether the staff member is assigned to the relevant session.
4. Whether the requested operation is allowed for that role.
5. Whether the frontend is using the correct authenticated account.

---

# Future Improvements

Potential future improvements include:

* Email notifications
* QR-code based check-in
* Automated reminders
* Advanced analytics
* Event calendar integration
* Export reports
* Audit logging
* Redis caching
* Background task processing
* Docker deployment
* CI/CD pipeline
* Cloud deployment
* Automated test suite
* Rate limiting
* Refresh token support
* Password reset functionality
* Email verification

---

# Project Status

The project currently provides the core functionality required for an event registration platform, including:

* Authentication
* Role-based access control
* Event management
* Session management
* Registration lifecycle
* Staff assignment
* Check-in
* Search and filtering
* Pagination
* CSV import/export
* Dashboard
* Capacity monitoring
* Registration history

The system is suitable for local development, demonstration, testing, and further feature development.

---

# Repository

GitHub Repository:

**Event Registration System**

```text
https://github.com/Hassara17/event-registration-system
```

---



# Live Demo

The Event Registration System is deployed and available online.

## Frontend

The React frontend is deployed on **Vercel**:

[Open Event Registration System Frontend](https://event-registration-system-g303ykami-hassan-20f1.vercel.app/login)

Use this link to access the application and test the user interface.

## Backend API

The FastAPI backend is deployed on **Render**:

[Open Backend API Documentation](https://event-registration-system-ogv7.onrender.com/docs)

The backend provides interactive **Swagger/OpenAPI documentation**, where you can view and test the available API endpoints.

### Deployment Architecture

```text
                    ┌─────────────────────────┐
                    │       Vercel            │
                    │    React + Vite         │
                    │      Frontend           │
                    └────────────┬────────────┘
                                 │
                                 │ HTTPS / REST API
                                 ▼
                    ┌─────────────────────────┐
                    │        Render           │
                    │       FastAPI           │
                    │        Backend          │
                    └────────────┬────────────┘
                                 │
                                 │ SQLAlchemy
                                 ▼
                    ┌─────────────────────────┐
                    │      Supabase           │
                    │        Database         │
                    └─────────────────────────┘
```

> **Note:** The frontend communicates with the deployed FastAPI backend through REST APIs. The backend API documentation can be used to test the API independently.

# License

This project is developed for educational and assignment purposes.

Unless otherwise specified, the project is not intended for production deployment without additional security, testing, monitoring, and infrastructure configuration.
