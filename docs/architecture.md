Where does each piece run?
Frontend

This React/Vite application runs locally in our browser during development:

http://localhost:5173

The browser is responsible for rendering the UI and making HTTP requests for the backend.

Backend

The FastAPI application runs locally as the API server.

It exposes endpoints such as:

/auth/login
/auth/me
/events
/sessions
/registrations
/dashboard
/capacity-alerts

The backend is responsible for authentication, role checking, validation, business rules, and database operations.

Database

The database runs as the persistent data store used by the FastAPI application. The backend communicates with it through SQLAlchemy.

Therefore, the browser never communicates directly with the database.

What is the request path for one representative user action, end to end?

A representative action is an attendee registering for a session.

1. User logs in

The attendee enters their email and password in the React login page.

The frontend sends:

POST /auth/login

with the credentials expected by the FastAPI authentication endpoint.

2. Backend authenticates the user

FastAPI verifies the credentials and returns a JWT access token.

The frontend stores the token and requests:

GET /auth/me

to obtain the authenticated user's information, including their role.

3. Attendee opens a session

The React frontend requests the session information from the backend, for example:

GET /sessions/{session_id}

The backend retrieves the session and its event information from the database.

4. Attendee submits registration

The registration form sends:

POST /registrations

The JWT is included in the request so the backend knows which authenticated user is making the request.

5. Backend validates the request

The backend checks the relevant business rules, including:

whether the session exists;
whether the user is authorized to perform the action;
whether the session has available capacity;
whether the registration conflicts with an existing registration;
whether the requested registration state is valid.

The capacity calculation includes registrations that are Reserved, Confirmed, or Checked In, as required by the assignment.

6. Database is updated

If the registration is valid, the backend creates the registration record through SQLAlchemy and records the corresponding registration history.

FastAPI
   ↓
Registration logic
   ↓
SQLAlchemy
   ↓
Database

If the operation violates a business rule, the backend rejects it and returns an appropriate error instead of relying on the frontend to prevent it.

7. Frontend displays the result

The React application receives the API response and updates the session/registration UI.

So the complete path is:

Attendee
   ↓
React Registration Form
   ↓
POST /registrations
   ↓
FastAPI authentication/authorization
   ↓
Registration business logic
   ↓
SQLAlchemy
   ↓
Database
   ↓
Registration + History
   ↓
FastAPI response
   ↓
React UI
   ↓
Attendee sees registration status

This same architecture is used for organizer and check-in staff operations; only the allowed actions differ according to the user's role.

What did you decide not to build, and why?

The implementation deliberately focuses on the requirements of the assignment rather than adding unrelated production features.

1. No separate microservices

The system uses one FastAPI backend instead of splitting authentication, registrations, events, notifications, etc. into separate services.

Why: The application is small enough that a modular monolithic backend is simpler to develop, test, and maintain.

2. No real-time WebSocket system

Capacity alerts and dashboard information are retrieved through normal API requests rather than implementing WebSockets.

Why: Real-time bidirectional communication was not required by the assignment. REST polling/API refreshes are sufficient for the implemented requirements.

3. No external email/SMS notification service

The system does not integrate an external email or SMS provider for registration confirmations, cancellations, or capacity alerts.

Why: Notifications through external providers were outside the core assignment requirements.

4. No payment system

The registration process does not include payment, invoices, or transaction processing.

Why: Event registration in this assignment is free and does not require payment processing.

5. No separate mobile application

There is no Android/iOS application.

Why: The assignment requires a web-based frontend, so a responsive React interface was sufficient.

6. No advanced distributed deployment infrastructure

The project is developed and tested as a frontend + backend application rather than introducing Kubernetes, load balancers, distributed caching, or other large-scale infrastructure.

Why: Those components would add operational complexity without being necessary for the assignment's functional requirements.