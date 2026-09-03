# AI prompts

This project was developed with the assistance of AI for understanding the existing backend, planning the frontend, implementing API integrations, debugging errors, and reviewing the completed requirements. I did not blindly accept generated code; I tested the changes against the running FastAPI backend and corrected issues when they appeared.

The prompts below are arranged approximately in the order in which they were used.

---

## 1. Understanding the existing backend and assignment requirements

### What I was trying to achieve

Before building the frontend, I needed to understand the existing FastAPI backend, its routes, models, roles, and the requirements of the Event Registration assignment.

### Prompt

> I have an existing FastAPI backend for an Event Registration System. Study the README and backend structure and explain the available APIs, authentication flow, user roles, events, sessions, registrations, staff assignment, dashboard, capacity alerts, and registration history. I want to build a React frontend around the existing backend, so identify exactly which frontend pages and API integrations are required.

### What I got

AI mapped the backend into functional areas such as:

- authentication
- events
- sessions
- registrations
- staff assignment
- dashboard
- capacity alerts
- registration history

It also identified that the frontend should communicate with the backend through REST APIs rather than duplicating business logic.

The proposed frontend structure included pages such as:

- Login
- Register
- Dashboard
- Events
- Event Details
- Session Details
- My Registrations
- Registration Search
- Registration Details
- My Sessions
- Alerts
- Profile

### What I corrected

I verified the suggested APIs against the actual FastAPI routes instead of assuming that every suggested endpoint existed.

For example, session creation was implemented according to the backend contract, where the backend expects query parameters rather than a JSON body.

I also kept server-side authorization as the source of truth instead of relying only on frontend visibility.

---

## 2. Building the React/Vite frontend structure

### What I was trying to achieve

I needed a clean React frontend that could communicate with the existing FastAPI backend.

### Prompt

> Build the frontend for this Event Registration System using React and Vite. Create a clean project structure with API modules, authentication context, protected routes, role-based routes, pages, components, and CSS. Use Axios for API communication and keep the code simple.

### What I got

AI proposed a structure separating:

- API functions
- React pages
- reusable components
- authentication context
- route protection
- CSS

The frontend was implemented with files such as:

```text
src/
├── api/
├── components/
├── context/
├── hooks/
├── pages/
└── routes/