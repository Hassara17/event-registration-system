# Plan

## How did you break the work into sessions?

I divided the implementation into several practical sessions based on the major parts of the assignment:

1. **Backend/API understanding**
   - Studied the existing FastAPI backend, API routes, authentication, roles, and assignment requirements.

2. **React/Vite setup**
   - Created the frontend structure and connected React/Vite with the existing backend API.

3. **Authentication and routing**
   - Implemented login, registration, JWT handling, protected routes, and role-based navigation.

4. **Events and sessions**
   - Implemented event pages and session management functionality.

5. **Registration lifecycle**
   - Implemented registration, confirmation, cancellation, check-in, capacity validation, search, filtering, and pagination.

6. **Staff assignment**
   - Implemented assigning and removing check-in staff from sessions and viewing assigned sessions.

7. **Dashboard and capacity alerts**
   - Added dashboard statistics, check-in chart, registration summaries, and capacity alerts.

8. **History, testing, and debugging**
   - Tested registration history, role restrictions, capacity rules, and the complete registration lifecycle.

9. **Documentation and GitHub**
   - Completed the required documentation and pushed the final project to GitHub.

## What order did you build in, and why that order?

I followed a dependency-based order:

```text
Backend/API Understanding
        ↓
React/Vite Setup
        ↓
Authentication
        ↓
Role-based Routing
        ↓
Events
        ↓
Sessions
        ↓
Registrations
        ↓
Staff Assignment
        ↓
Dashboard & Alerts
        ↓
History & Testing
        ↓
Documentation & GitHub

I started by understanding the backend because the frontend had to work with the existing API. Authentication was implemented before the protected features because the application depends on the user's identity and role.

Events were built before sessions because sessions belong to events. Sessions were then implemented before registrations because registrations belong to sessions.

After the main registration flow was working, I added staff assignment, dashboard functionality, capacity alerts, and history. Testing and debugging were performed throughout the implementation rather than only at the end.

What did you estimate versus what it actually took?
Work	Initial estimate	Actual effort
Backend/API understanding	1 hour	1 hour
React/Vite setup	1 hour	1 hour
Authentication & routing	1.5 hours	1.5 hours
Events & sessions	2 hours	2 hours
Registration lifecycle	2 hours	2 hours
Staff assignment	1 hour	1 hour
Dashboard & alerts	1 hour	1 hour
History/search/import/export/testing	1.5 hours	1.5 hours
Documentation/GitHub cleanup	1 hour	1 hour
Total	12 hours	12 hours

The main effort was spent on implementing and integrating the required functionality rather than adding unnecessary features. The final implementation was completed within approximately 12 hours.

What did you cut when you ran short?

I did not cut any of the 10 core assignment requirements. Instead, I prioritized the required functionality over optional features.

Features that were not implemented because they were outside the assignment scope included:

Advanced UI animations
Separate mobile applications
Real-time WebSocket notifications
External email/SMS notification services
Payment integration
Complex deployment infrastructure
Other non-essential third-party services

The priority was to complete the required functionality correctly, especially authentication, role-based authorization, registration lifecycle, capacity management, staff assignment, registration history, dashboard functionality, capacity alerts, and testing.