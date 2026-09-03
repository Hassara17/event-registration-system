Decisions
Decision 1
Chose: Use a React + Vite frontend for the web application.
Rejected: Building the frontend with plain HTML/CSS/JavaScript or using a heavier framework.
Why: React made it easier to organize the application into reusable pages and components and manage authentication, role-based navigation, forms, and API-driven state. Vite also kept the development setup simple and fast.
Decision 2
Chose: Keep the existing FastAPI backend and build the frontend around its REST API.
Rejected: Rewriting the backend or moving the business logic into the React application.
Why: The backend already provided the required API structure and business logic. Keeping it allowed the frontend to remain focused on presentation and user interaction while important validation and authorization stayed server-side.
Decision 3
Chose: Use JWT-based authentication with the access token stored by the frontend and sent with API requests.
Rejected: Keeping authentication only in React state or using session information without a token-based API authentication mechanism.
Why: The application has multiple roles and protected API endpoints. JWT allows the FastAPI backend to authenticate each request independently and enforce permissions even if someone bypasses the frontend UI.
Decision 4
Chose: Enforce organizer/check-in-staff permissions on the backend, while also hiding or showing appropriate frontend actions based on the user's role.
Rejected: Relying only on frontend role checks.
Why: Frontend restrictions are only a usability feature and can be bypassed by directly calling an API. Server-side authorization is therefore required for operations such as creating sessions, assigning staff, managing registrations, and accessing organizer functionality.
Decision 5
Chose: Represent staff-to-session assignment as a many-to-many relationship using a separate session_staff association table.
Rejected: Storing a single staff_id directly inside the session or storing multiple staff IDs as a list/string.
Why: A session can have multiple check-in staff members, and one staff member can be assigned to multiple sessions. A separate association table represents this relationship cleanly and allows assignments to be added or removed independently.
Decision 6
Chose: Use the registration lifecycle Reserved → Confirmed → Checked In, with cancellation and expiration handled as separate states/transitions.
Rejected: Treating registration as a simple boolean such as registered = true/false.
Why: The assignment requires capacity management, temporary reservations, confirmation, check-in, cancellation, expiration, and rejection of invalid transitions. Explicit statuses make those rules easier to enforce and audit.
Decision 7
Chose: Keep registration history as immutable records instead of allowing the current registration record to contain the entire history.
Rejected: Updating the registration row without keeping a separate history of previous states.
Why: The assignment requires an audit trail containing status changes, the previous/new status, actor, notes, and creation information. Separate history records preserve what happened even after the registration's current status changes.
Decision 8
Chose: Add a dedicated capacity-alert mechanism rather than calculating an alert only in the frontend.
Rejected: Showing a warning based only on the number displayed in the React session page.
Why: Capacity is a server-side business condition. Keeping the alert state on the backend allows the organizer's alert view and navigation badge to remain consistent and allows an alert to return when a previously full session becomes full again.
Decision 9
Chose: Use server-side search, filtering, sorting, and pagination for registration lists.
Rejected: Downloading all registrations to React and performing filtering/pagination in the browser.
Why: Registration data can grow significantly. Server-side processing reduces the amount of data transferred to the browser and keeps the API usable as the number of registrations increases.
Decision 10
Chose: Initially used a temporary frontend route for /sessions, then changed it to the dedicated session-management flow once the session requirements were implemented.
Rejected: Keeping the temporary placeholder route permanently.
Why: During early frontend development, using an existing page as a temporary route allowed the rest of the application to be connected and tested before the dedicated session UI was finished. Once the session functionality was implemented, keeping the placeholder would have created confusing navigation and duplicated responsibilities