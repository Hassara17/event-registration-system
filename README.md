# README.md

````md
# Event Registration System

A full-stack event registration and session management system built with a **React + Vite frontend** and a **FastAPI backend**.

The system supports multiple user roles, event and session management, registration lifecycle management, staff assignment, CSV import/export, dashboards, registration history, and capacity alerts.

---

## Features

### 1. Authentication & Role Management

The application supports three roles:

- **Organizer**
- **Check-in Staff**
- **Attendee**

Authentication is handled using JWT-based authentication.

#### Organizer

Organizers can:

- Create events
- Edit events
- Archive and restore events
- Create sessions
- Edit sessions
- Delete sessions
- Set session capacity
- Create registrations
- Confirm registrations
- Cancel registrations
- Check in attendees
- Import registrations using CSV
- Export session check-in sheets
- Assign check-in staff to sessions
- Remove staff from sessions
- View registration statistics
- View registration history
- Manage capacity alerts

#### Check-in Staff

Check-in staff can:

- View assigned sessions
- View registrations for assigned sessions
- Confirm registrations
- Cancel registrations
- Check in attendees
- View session information

They cannot:

- Create events
- Create sessions
- Change session capacity
- Assign staff

#### Attendee

Attendees can:

- Register/login
- View events
- View sessions
- Register for sessions
- View their registrations
- Cancel eligible registrations
- View their registration history
- View their profile

---

# Registration Lifecycle

Registrations follow the lifecycle:

```text
Reserved
    |
    +------> Cancelled
    |
    +------> Expired
    |
    v
Confirmed
    |
    +------> Cancelled
    |
    v
Checked In
````

### Rules

* `Reserved`, `Confirmed`, and `Checked In` count toward session capacity.
* A session cannot exceed its configured capacity.
* Reserved registrations can expire after the holding period.
* Reserved registrations can be cancelled.
* Confirmed registrations can be cancelled.
* Checked-in registrations cannot be cancelled.
* Invalid state transitions are rejected by the backend.
* Registration history is immutable.

---

# Event Management

An event contains:

* Title
* Description
* Start date
* End date
* Venue
* Organizer
* Archive status

Events can be:

* Created
* Updated
* Archived
* Restored
* Deleted

Archived events are hidden from normal views while their sessions and registrations remain stored.

---

# Session Management

Each session belongs to an event.

A session contains:

* Event
* Title
* Start time
* Duration
* Location
* Capacity

Organizers can create, update, and delete sessions.

The system also provides session-level:

* Registration statistics
* Registration management
* Staff assignment
* CSV import
* CSV export

---

# Staff Assignment

The system supports a many-to-many relationship between:

```text
Users <----> Sessions
```

through the `session_staff` association table.

A staff member can be assigned to multiple sessions.

A session can have multiple check-in staff members.

Only organizers can assign or remove staff.

---

# Search, Filtering & Pagination

Registration management supports:

### Search

* Attendee name
* Attendee email

### Filters

* Event
* Session
* Registration status

### Sorting

Registrations can be sorted by:

* Reserved time
* Status
* Session

### Pagination

Registration lists use server-side pagination and return the total number of matching records.

---

# CSV Import & Export

## CSV Import

Organizers can import registrations for a session using CSV.

The import process handles rows independently.

Each row can be:

* Created
* Duplicate
* Rejected

Rejected rows include a reason.

Invalid rows do not prevent valid rows from being imported.

## CSV Export

Organizers can export a session check-in sheet as CSV.

The exported file contains registration information useful during event check-in.

---

# Dashboard

The dashboard provides an overview of event registration activity.

It includes:

* Sessions today
* Checked-in attendees today
* Expired registrations this week
* Sessions at capacity
* Registration status breakdown
* Registrations by session
* 14-day check-in activity chart

Dashboard information is retrieved from the backend rather than being calculated only on the frontend.

---

# Capacity Alerts

The system detects sessions that have reached capacity.

Capacity alerts are available to organizers.

When a session becomes full:

```text
Session reaches capacity
        |
        v
Capacity alert created
        |
        v
Organizer sees alert
```

Organizers can dismiss alerts.

If seats become available and the session becomes full again, the alert can appear again.

---

# Registration History

Registration changes are recorded in an immutable history.

The history records important actions such as:

* Registration creation
* Status changes
* Previous status
* New status
* Actor
* Notes
* Timestamp

The history is not edited or deleted when the current registration changes.

---

# Technology Stack

## Frontend

* React
* Vite
* React Router
* Axios
* CSS

## Backend

* Python
* FastAPI
* SQLAlchemy
* JWT Authentication
* Pydantic

## Database

* Relational database
* SQLAlchemy ORM

---

# Architecture

```text
                 ┌──────────────────────┐
                 │      React/Vite      │
                 │      Frontend        │
                 └──────────┬───────────┘
                            │
                         Axios
                            │
                            ▼
                 ┌──────────────────────┐
                 │       FastAPI        │
                 │       Backend        │
                 └──────────┬───────────┘
                            │
                 ┌──────────┴───────────┐
                 │                      │
                 ▼                      ▼
          ┌──────────────┐       ┌──────────────┐
          │  Services /  │       │ JWT / Role   │
          │ Business     │       │ Authorization│
          │ Logic        │       └──────────────┘
          └──────┬───────┘
                 │
                 ▼
          ┌──────────────┐
          │ SQLAlchemy   │
          │ ORM          │
          └──────┬───────┘
                 │
                 ▼
          ┌──────────────┐
          │ Relational   │
          │ Database     │
          └──────────────┘
```

---

# Project Structure

```text
event-registration-system/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── core/
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── ...
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── context/
│   │   ├── pages/
│   │   ├── routes/
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   ├── package.json
│   └── ...
│
├── docs/
│   ├── architecture.md
│   ├── schema.md
│   ├── plan.md
│   ├── decisions.md
│   └── ai-prompts.md
│
└── README.md
```

---

# Backend API

The backend is built using FastAPI.

Main API groups include:

| Area            | Endpoint examples                           |
| --------------- | ------------------------------------------- |
| Authentication  | `/auth/register`, `/auth/login`, `/auth/me` |
| Events          | `/events`, `/events/{event_id}`             |
| Sessions        | `/sessions`, `/sessions/{session_id}`       |
| Registrations   | `/registrations`, `/registrations/search`   |
| Staff           | `/sessions/{session_id}/staff/{staff_id}`   |
| Dashboard       | `/dashboard`                                |
| Capacity Alerts | `/capacity-alerts`                          |
| Users           | `/users`                                    |

The backend is responsible for authentication, authorization, business rules, validation, capacity enforcement, and database operations.

---

# Running the Project

## Prerequisites

Install:

* Python 3.10+
* Node.js
* npm
* A configured relational database

---

# Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

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

Configure the required database/environment variables according to the backend configuration.

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The backend will normally run at:

```text
http://127.0.0.1:8000
```

FastAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

# Frontend Setup

Navigate to the frontend:

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

The frontend will normally run at:

```text
http://localhost:5173
```

The backend CORS configuration allows the frontend to communicate from:

```text
http://localhost:5173
http://127.0.0.1:8000/docs
```

---

# Authentication Flow

The login flow is:

```text
User
 |
 | email + password
 v
React Login Page
 |
 | POST /auth/login
 v
FastAPI
 |
 | validate credentials
 v
JWT Access Token
 |
 v
React
 |
 | store token
 v
GET /auth/me
 |
 v
Authenticated User
```

The frontend uses the authenticated user's role to control the available UI.

The backend independently enforces authorization so frontend restrictions cannot be bypassed by simply calling an API manually.

---

# Role-Based Access

The application uses role-aware routing and UI.

Example:

```text
                  Login
                    |
          ┌─────────┼─────────┐
          │         │         │
          ▼         ▼         ▼
      Organizer    Staff   Attendee
          │         │         │
          ▼         ▼         ▼
      Dashboard  Dashboard  Profile
```

Frontend role checks improve usability, while backend authorization provides the actual security boundary.

---
## Creating Demo Organizer and Check-in Staff

For security reasons, the public registration endpoint creates only `attendee` accounts.  
Organizer and check-in staff accounts must be created using the seed script.

From the `backend` directory, run:

```bash
python seed.py

This creates the following demo accounts:

Role	Email	Password
Organizer	organizer@example.com	Organizer@123
Check-in Staff	staff@example.com	Staff@123

The seed script is safe to run multiple times because it checks whether the user already exists before creating a new account.

Important

Run the seed script after configuring the database connection in the backend .env file.

cd backend
python seed.py

After the accounts are created, you can use the organizer account to access organizer-only features such as event/session management, staff assignment, and dashboard functionality.


### I also recommend adding it near

```text
Installation / Setup
       ↓
Database Configuration
       ↓
Run Migrations
       ↓
Create Demo Users   ← add here
       ↓
Run Backend
       ↓
Run Frontend



# Example Registration Flow

An attendee registers for a session:

```text
Attendee
   |
   | Select session
   v
Session Details
   |
   | Register
   v
POST /registrations
   |
   v
Backend validation
   |
   ├── Session exists?
   ├── Capacity available?
   ├── Registration allowed?
   └── Valid user?
   |
   v
Create Reserved registration
   |
   v
Registration history created
   |
   v
Response returned to frontend
```

An organizer/staff member can then move the registration through the allowed lifecycle.

---

# Security

The application uses server-side authorization for protected operations.

Important security principles include:

* JWT authentication
* Password authentication through the backend
* Role-based authorization
* Backend-side capacity validation
* Backend-side registration state validation
* Session staff authorization
* Organizer-only administrative operations
* No reliance on frontend-only permissions

A user hiding a button in the frontend does not grant or remove backend permissions.

---

# Error Handling

The frontend displays backend error messages where available.

Typical errors include:

* Invalid login credentials
* Unauthorized access
* Session not found
* Event not found
* Session at capacity
* Invalid registration transition
* Registration already exists
* Invalid CSV row
* Staff assignment failure

The backend returns appropriate HTTP errors and reasons which are displayed by the frontend.

---

# Development Decisions

Some design decisions were intentionally made to keep the system simple and maintainable.

### React + Vite

React with Vite was selected for a lightweight frontend development environment.

### Existing FastAPI Backend

The existing backend API was reused instead of rewriting the backend.

### JWT Authentication

JWT authentication provides a straightforward stateless authentication mechanism.

### Backend Authorization

Authorization is enforced by the backend instead of relying only on frontend route restrictions.

### Many-to-Many Staff Assignment

A separate `session_staff` table allows staff members to be assigned to multiple sessions and sessions to have multiple staff members.

### Explicit Registration Lifecycle

Registration states are represented explicitly instead of using multiple unrelated boolean fields.

### Immutable Registration History

Registration history is stored separately so that changes remain auditable.

### Server-Side Search and Pagination

Filtering, sorting and pagination are performed by the backend to avoid loading large registration datasets into the browser.

---

# Documentation

Additional project documentation is available in the `docs/` directory.

### Architecture

```text
docs/architecture.md
```

Describes:

* System components
* Communication between components
* Runtime locations
* End-to-end request flow
* Features intentionally not implemented

### Database Schema

```text
docs/schema.md
```

Describes:

* Database tables
* Columns
* Relationships
* Constraints
* Denormalization
* Scaling considerations

### Development Plan

```text
docs/plan.md
```

Describes:

* Development sessions
* Work ordering
* Estimated effort
* Actual effort
* Scope decisions

### Technical Decisions

```text
docs/decisions.md
```

Contains important implementation decisions and alternatives considered.

### AI Usage

```text
docs/ai-prompts.md
```

Documents AI-assisted development prompts, outputs, and corrections.

---

# Testing Checklist

The following scenarios should be tested before deployment:

## Authentication

* [ ] Register attendee
* [ ] Login with valid credentials
* [ ] Reject invalid credentials
* [ ] Logout
* [ ] Restore authenticated session after refresh

## Organizer

* [ ] Create event
* [ ] Edit event
* [ ] Archive event
* [ ] Restore event
* [ ] Create session
* [ ] Edit session
* [ ] Delete session
* [ ] Assign staff
* [ ] Remove staff

## Attendee

* [ ] View events
* [ ] View sessions
* [ ] Register for session
* [ ] View registration
* [ ] Cancel eligible registration
* [ ] View registration history

## Registration

* [ ] Reserved registration
* [ ] Confirm registration
* [ ] Check in registration
* [ ] Cancel registration
* [ ] Reject invalid state transition
* [ ] Reject registration when capacity is full
* [ ] Verify expiration

## Staff

* [ ] View assigned sessions
* [ ] View assigned registrations
* [ ] Confirm registration
* [ ] Check in attendee
* [ ] Verify staff cannot create sessions
* [ ] Verify staff cannot modify capacity

## CSV

* [ ] Import valid rows
* [ ] Handle duplicate rows
* [ ] Handle invalid rows
* [ ] Verify valid rows still import
* [ ] Export check-in sheet

## Dashboard

* [ ] Sessions today
* [ ] Checked-in today
* [ ] Expired this week
* [ ] Full sessions
* [ ] Status breakdown
* [ ] Session registration statistics
* [ ] 14-day check-in chart

## Capacity Alerts

* [ ] Alert when session becomes full
* [ ] Dismiss alert
* [ ] Free a seat
* [ ] Fill session again
* [ ] Verify alert appears again

---

# API Documentation

Once the backend is running, interactive API documentation is available through FastAPI:

```text
/docs
```

This can be used to inspect and manually test the available endpoints.

---

# Future Improvements

Possible future improvements include:

* Email notifications
* SMS notifications
* QR-code based check-in
* Real-time dashboard updates
* Redis caching
* Background jobs
* Advanced analytics
* Automated deployment
* Docker-based deployment
* Automated unit/integration tests
* CI/CD pipeline
* Production monitoring

These were kept outside the current scope to focus on the required event registration functionality.

---

# Project Status

The current implementation covers the required event registration workflow including:

* Authentication
* Role-based access
* Events
* Sessions
* Registration lifecycle
* Staff assignment
* Search/filtering/pagination
* CSV import/export
* Dashboard
* Registration history
* Capacity alerts



# License

This project was developed as part of a software development assignment.


