# Schema

The application uses a relational database accessed through SQLAlchemy. The main data is organized around users, events, sessions, registrations, registration history, staff assignments, and capacity alerts.

## Table by table: what columns and types does each one have?

### `users`

The `users` table stores the application's authenticated users.

| Column | Type | Purpose |
|---|---|---|
| `id` | Integer | Primary key identifying the user |
| `name` | String | User's name |
| `email` | String | User's email address used for authentication |
| `hashed_password` | String | Hashed password rather than storing the plain password |
| `role` | String | User role such as `attendee`, `organizer`, or `checkin_staff` |

The user role is used by the application to determine which API operations the user is allowed to perform.

---

### `events`

The `events` table stores the main event information.

| Column | Type | Purpose |
|---|---|---|
| `id` | Integer | Primary key |
| `title` | String | Event title/name |
| `description` | String/Text | Event description |
| `start_date` | Date/DateTime | Event start date |
| `end_date` | Date/DateTime | Event end date |
| `venue` | String | Event venue |
| `organizer_id` | Integer | Foreign key referencing the organizer/user |
| `is_archived` | Boolean | Indicates whether the event is archived |

An archived event is retained in the database instead of being deleted. The application hides archived events from the normal event views.

---

### `sessions`

The `sessions` table stores individual sessions belonging to an event.

| Column | Type | Purpose |
|---|---|---|
| `id` | Integer | Primary key |
| `event_id` | Integer | Foreign key referencing `events.id` |
| `title` | String | Session title |
| `start_time` | DateTime | Session starting time |
| `duration` | Integer | Duration of the session |
| `location` | String | Location of the session within the event venue |
| `capacity` | Integer | Maximum number of registrations allowed |

A session belongs to exactly one event.

---

### `registrations`

The `registrations` table stores an attendee's registration for a session.

| Column | Type | Purpose |
|---|---|---|
| `id` | Integer | Primary key |
| `user_id` | Integer | Foreign key referencing the registered user |
| `session_id` | Integer | Foreign key referencing the session |
| `attendee_name` | String | Name recorded for the attendee |
| `attendee_email` | String | Email recorded for the attendee |
| `status` | String | Current registration status |
| `reserved_at` | DateTime | Time at which the registration was reserved |
| `confirmed_at` | DateTime | Time at which it was confirmed |
| `checked_in_at` | DateTime | Time at which the attendee checked in |
| `cancelled_at` | DateTime | Time at which the registration was cancelled |
| `expired_at` | DateTime | Time at which a reservation expired |

The status represents the registration lifecycle:

```text
Reserved
   ↓
Confirmed
   ↓
Checked In

Other terminal states such as Cancelled and Expired are used when a reservation is cancelled or its holding period expires.

The registration table also keeps attendee name and email so that the registration represents the information associated with that particular registration.

registration_history

The registration_history table stores the immutable audit trail for registrations.

It records events such as registration creation and status changes.

The history contains information for:

the registration involved;
previous status;
new status;
the actor who performed the action;
when the action occurred;
notes associated with the action.

The history is intentionally append-only from the application's perspective. Existing history entries are not edited or deleted.

session_staff

The session_staff table is an association table between users and sessions.

Column	Type	Purpose
session_id	Integer	Foreign key referencing sessions.id
staff_id	Integer	Foreign key referencing users.id

Both columns form the composite primary key.

The database definition uses cascading foreign keys so that an assignment does not remain after its referenced session or user is removed.

This table is used because a session can have multiple check-in staff members and one staff member can work on multiple sessions.

capacity_alerts

The capacity_alerts table stores the alert state associated with sessions that reach capacity.

The alert mechanism allows organizers to see sessions that are currently full and dismiss the corresponding alert.

The important relationship is with the session whose capacity has been reached.

Which relationships are one-to-many, and which are many-to-many?
One-to-many relationships
User → Events

One organizer can create multiple events.

User
  │
  └──< Event

The event stores the organizer's ID.

Event → Sessions

One event can contain multiple sessions.

Event
  │
  ├── Session
  ├── Session
  └── Session

Each session contains event_id, so every session belongs to one event.

Session → Registrations

One session can have many registrations.

Session
  │
  ├── Registration
  ├── Registration
  └── Registration

Each registration contains session_id.

User → Registrations

One user can have registrations for multiple sessions.

User
  │
  ├── Registration
  ├── Registration
  └── Registration

Each registration contains user_id.

Registration → Registration History

One registration can have multiple history records.

Registration
     │
     ├── History
     ├── History
     ├── History
     └── History

This allows the complete lifecycle of a registration to be retained instead of overwriting previous states.

Many-to-many relationship
Users ↔ Sessions

Check-in staff and sessions have a many-to-many relationship.

User
  │
  ├──────────────┐
  │              │
  ▼              ▼
SessionStaff → Sessions

A staff member can be assigned to multiple sessions, while a session can have multiple staff members.

The session_staff table resolves this many-to-many relationship:

users
  │
  │ staff_id
  ▼
session_staff
  ▲
  │ session_id
  │
sessions

This is preferable to storing multiple staff IDs in one session row.

Which constraints are enforced by the database, and which by application code?

I used the database mainly for structural integrity and the application for business rules.

Database-level constraints

The database is responsible for things that should remain true regardless of which part of the application performs the operation.

Examples include:

Primary keys uniquely identify records.
Foreign keys connect related records.
session_staff.session_id references the sessions table.
session_staff.staff_id references the users table.
The combination of session_id and staff_id identifies a unique staff assignment.
Cascading deletes are used for relevant session/user assignment relationships.

For example, session_staff uses both session_id and staff_id as primary-key columns, preventing the same staff member from being assigned to the same session more than once.

Application-level constraints

Business rules are handled by FastAPI/service logic because they require context and decisions rather than simple column validation.

Examples include:

Only organizers can create or modify events and sessions.
Check-in staff can only operate on their assigned sessions.
Attendees cannot access organizer registration searches.
A session cannot exceed its capacity.
Reserved → Confirmed is allowed.
Confirmed → Checked In is allowed.
A Checked In registration cannot be cancelled.
A Reserved registration can expire after the holding window.
A cancelled or expired registration frees capacity.
Only valid registration status transitions are accepted.
Capacity alerts are generated/dismissed according to application behaviour.
Archived events are hidden from normal views but retained.

These rules are implemented in application code because they depend on multiple records and the current user's role and action.

For example, determining whether a session is full requires counting registrations with the relevant active statuses rather than simply validating one database column.

The registration search also performs role-based visibility, attendee name/email search, filtering, sorting, and pagination in the backend rather than loading all registrations into the frontend.

Why was the line drawn this way?

The database is used to protect data integrity, while the application is responsible for business behaviour.

For example:

Database:
"Does this session ID actually exist?"

Application:
"Is this user allowed to register for this session?"

Database:
"Can this registration reference a non-existent session?"

Application:
"Is there still capacity for this session?"

Database:
"Can the same session/staff pair exist twice?"

Application:
"Is this organizer allowed to assign this staff member?"

This separation keeps the database rules simple and reusable while allowing the FastAPI services to implement the more complicated assignment-specific rules.

What did you deliberately denormalise?

The main deliberate denormalisation is in the registrations table.

The registration stores:

attendee_name
attendee_email

even though the registration also has a user_id that identifies the user.

This means some user information is duplicated.

The reason is that the registration represents the attendee information associated with that particular registration. It also makes registration search and CSV import/export straightforward because the registration already contains the name and email that should be displayed.

The registration search directly searches:

Registration.attendee_name
Registration.attendee_email

rather than requiring the frontend to retrieve user records separately.

This was a practical choice for the assignment rather than an attempt to completely eliminate duplicated data.

The registration API also returns these fields directly as part of a registration result.

What would break first if this had 100x the data?

The basic relational design would still work, but some operations would become noticeably more expensive.

1. Registration search would be the first major pressure point

The registration search supports:

attendee name search;
attendee email search;
event filtering;
session filtering;
status filtering;
sorting;
pagination.

The current implementation calculates the total number of matching records before applying offset and limit.

With 100x more registrations, the COUNT operation and filtered searches could become expensive, especially for broad searches.

I would address this with appropriate database indexes and potentially more efficient search strategies.

2. Offset-based pagination would become less efficient

The current implementation uses:

OFFSET
LIMIT

for pagination.

This is simple and appropriate for the current assignment, but very large offsets can become expensive because the database may have to scan through many earlier rows before returning the requested page.

At much larger scale, cursor/keyset pagination would be a better option.

3. Dashboard aggregation could become expensive

The dashboard calculates statistics such as:

registrations by status;
registrations by session;
today's check-ins;
expired registrations;
sessions at capacity;
daily check-ins.

With substantially more registration history, repeatedly calculating these values from raw registration records could become expensive.

At that scale I would consider:

database indexes;
optimized aggregation queries;
cached dashboard results;
precomputed summary tables where appropriate.
4. Registration history would grow rapidly

Every registration can produce multiple history records.

Therefore:

Registrations × status changes = History records

At 100x the number of registrations, the history table could become considerably larger than the registration table.

The history should remain immutable, but older records could eventually require archival/partitioning strategies depending on the retention requirements.

5. Capacity calculations could become expensive

Capacity checking depends on the registrations associated with a session.

At larger scale, the registration status/session indexes would become important because capacity checks and registration searches repeatedly query these fields.