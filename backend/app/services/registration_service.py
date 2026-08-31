from datetime import datetime, timedelta

import csv
import io

from fastapi import HTTPException, status
from sqlalchemy import asc, desc, func, or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.event import Event
from app.models.registration import Registration
from app.models.session import Session as EventSession
from app.models.session_staff import SessionStaff
from app.models.registration_history import RegistrationHistory

from app.services.registration_history_service import (
    create_history_entry,
)

from app.services.capacity_alert_service import (
    update_capacity_alert,
)


# ============================================================
# ACTIVE REGISTRATION STATUSES
# ============================================================

ACTIVE_STATUSES = {
    "reserved",
    "confirmed",
    "checked_in",
}


# ============================================================
# ALL REGISTRATION STATUSES
# ============================================================

VALID_STATUSES = {
    "reserved",
    "confirmed",
    "checked_in",
    "cancelled",
    "expired",
}


# ============================================================
# RESERVATION HOLDING WINDOW
# ============================================================

HOLDING_WINDOW_MINUTES = settings.reservation_hold_minutes


# ============================================================
# EXPIRE OLD RESERVATIONS
# ============================================================

def expire_old_reservations(
    db: Session,
) -> int:
    """
    Expire all Reserved registrations whose holding window
    has elapsed.

    Expired registrations no longer occupy seats.

    Goal 9:
        Every automatic expiration creates a registration
        history entry.

    Goal 10:
        Capacity alerts are refreshed for every affected
        session.

    Returns:
        Number of registrations expired.
    """

    expiration_time = (
        datetime.utcnow()
        - timedelta(minutes=HOLDING_WINDOW_MINUTES)
    )

    registrations = (
        db.query(Registration)
        .filter(
            Registration.status == "reserved",
            Registration.reserved_at <= expiration_time,
        )
        .all()
    )

    if not registrations:
        return 0

    now = datetime.utcnow()

    # Keep track of sessions affected by expiration.
    affected_session_ids = set()

    for registration in registrations:
        old_status = registration.status

        registration.status = "expired"
        registration.expired_at = now

        affected_session_ids.add(
            registration.session_id
        )

        # ----------------------------------------------------
        # GOAL 9 — REGISTRATION HISTORY
        # ----------------------------------------------------

        create_history_entry(
            db=db,
            registration_id=registration.id,
            action="expired",
            actor_user_id=None,
            old_status=old_status,
            new_status="expired",
            note="Registration automatically expired after the reservation holding window elapsed",
        )

    # Commit registration + history entries together.
    db.commit()

    # --------------------------------------------------------
    # GOAL 10 — UPDATE CAPACITY ALERTS
    # --------------------------------------------------------

    for session_id in affected_session_ids:
        update_capacity_alert(
            db=db,
            session_id=session_id,
        )

    return len(registrations)


# ============================================================
# CREATE REGISTRATION
# ============================================================

def create_registration(
    db: Session,
    session_id: int,
    user_id: int,
    attendee_name: str,
    attendee_email: str,
) -> Registration:
    """
    Create a new Reserved registration.

    Seat calculation:

        Reserved
        + Confirmed
        + Checked In

    All three statuses occupy a seat.

    A database row lock is used on the session so that
    concurrent reservations cannot oversell capacity.

    Goal 9:
        Creates an initial registration history entry.
    """

    # --------------------------------------------------------
    # Expire old reservations first
    # --------------------------------------------------------

    expire_old_reservations(db)

    # --------------------------------------------------------
    # Lock session row
    # --------------------------------------------------------

    event_session = (
        db.query(EventSession)
        .filter(
            EventSession.id == session_id,
        )
        .with_for_update()
        .first()
    )

    if event_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # --------------------------------------------------------
    # Find parent event
    # --------------------------------------------------------

    event = (
        db.query(Event)
        .filter(
            Event.id == event_session.event_id,
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    # --------------------------------------------------------
    # Event must be published
    # --------------------------------------------------------

    if not event.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is not published",
        )

    # --------------------------------------------------------
    # Archived event cannot accept registrations
    # --------------------------------------------------------

    if event.is_archived:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is archived",
        )

    # --------------------------------------------------------
    # Session must not have started
    # --------------------------------------------------------

    now = datetime.utcnow()

    if event_session.start_time <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Registration is closed because the session "
                "has already started or passed"
            ),
        )

    # --------------------------------------------------------
    # Prevent duplicate active registration
    # --------------------------------------------------------

    existing_registration = (
        db.query(Registration)
        .filter(
            Registration.user_id == user_id,
            Registration.session_id == session_id,
            Registration.status.in_(ACTIVE_STATUSES),
        )
        .first()
    )

    if existing_registration is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "You are already registered "
                "for this session"
            ),
        )

    # --------------------------------------------------------
    # Count occupied seats
    # --------------------------------------------------------

    registration_count = (
        db.query(func.count(Registration.id))
        .filter(
            Registration.session_id == session_id,
            Registration.status.in_(ACTIVE_STATUSES),
        )
        .scalar()
        or 0
    )

    # --------------------------------------------------------
    # Capacity check
    # --------------------------------------------------------

    if registration_count >= event_session.capacity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Session capacity is full",
        )

    # --------------------------------------------------------
    # Create reservation
    # --------------------------------------------------------

    registration = Registration(
        user_id=user_id,
        session_id=session_id,
        attendee_name=attendee_name.strip(),
        attendee_email=attendee_email.lower().strip(),
        status="reserved",
        reserved_at=now,
    )

    db.add(registration)

    # Flush first so registration.id is available for
    # the history record.
    db.flush()

    # --------------------------------------------------------
    # GOAL 9 — REGISTRATION HISTORY
    # --------------------------------------------------------

    create_history_entry(
        db=db,
        registration_id=registration.id,
        action="reserved",
        actor_user_id=user_id,
        old_status=None,
        new_status="reserved",
        note="Registration created",
    )

    # Commit registration + history atomically.
    db.commit()

    db.refresh(registration)

    # --------------------------------------------------------
    # GOAL 10 — UPDATE CAPACITY ALERT
    # --------------------------------------------------------

    update_capacity_alert(
        db=db,
        session_id=session_id,
    )

    return registration


# ============================================================
# GET USER REGISTRATIONS
# ============================================================

def get_user_registrations(
    db: Session,
    user_id: int,
) -> list[Registration]:
    """
    Return all active registrations for the current user.
    """

    expire_old_reservations(db)

    return (
        db.query(Registration)
        .filter(
            Registration.user_id == user_id,
            Registration.status.in_(ACTIVE_STATUSES),
        )
        .order_by(
            Registration.reserved_at.desc()
        )
        .all()
    )


# ============================================================
# GET USER REGISTRATION HISTORY
# ============================================================

def get_user_registration_history(
    db: Session,
    user_id: int,
) -> list[dict]:
    """
    Return the complete registration history for the user.

    This returns registration records including their current
    status and timestamps.
    """

    expire_old_reservations(db)

    registrations = (
        db.query(
            Registration,
            EventSession,
            Event,
        )
        .join(
            EventSession,
            Registration.session_id == EventSession.id,
        )
        .join(
            Event,
            EventSession.event_id == Event.id,
        )
        .filter(
            Registration.user_id == user_id,
        )
        .order_by(
            Registration.reserved_at.desc()
        )
        .all()
    )

    history = []

    for registration, event_session, event in registrations:
        history.append(
            {
                "id": registration.id,
                "session_id": event_session.id,
                "session_title": event_session.title,
                "event_id": event.id,
                "event_title": event.title,
                "venue": event.venue,
                "attendee_name": registration.attendee_name,
                "attendee_email": registration.attendee_email,
                "start_time": event_session.start_time,
                "status": registration.status,
                "reserved_at": registration.reserved_at,
                "confirmed_at": registration.confirmed_at,
                "checked_in_at": registration.checked_in_at,
                "cancelled_at": registration.cancelled_at,
                "expired_at": registration.expired_at,
            }
        )

    return history


# ============================================================
# GET REGISTRATION
# ============================================================

def get_registration(
    db: Session,
    registration_id: int,
) -> Registration | None:
    return (
        db.query(Registration)
        .filter(
            Registration.id == registration_id,
        )
        .first()
    )


# ============================================================
# SEARCH REGISTRATIONS - GOAL 6
# ============================================================

def search_registrations(
    db: Session,
    viewer,
    search: str | None = None,
    event_id: int | None = None,
    session_id: int | None = None,
    registration_status: str | None = None,
    sort_by: str = "reserved_at",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """
    Search registrations visible to the current user.

    Organizer:
        Can see registrations from sessions belonging
        to events owned by the organizer.

    Check-in staff:
        Can see registrations only from sessions assigned
        to that staff member.
    """

    # ========================================================
    # VALIDATE PAGINATION
    # ========================================================

    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be greater than or equal to 1",
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size must be between 1 and 100",
        )

    # ========================================================
    # VALIDATE STATUS
    # ========================================================

    if (
        registration_status is not None
        and registration_status not in VALID_STATUSES
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid registration status "
                f"'{registration_status}'"
            ),
        )

    # ========================================================
    # VALIDATE SORTING
    # ========================================================

    allowed_sort_fields = {
        "reserved_at": Registration.reserved_at,
        "status": Registration.status,
        "session": EventSession.title,
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid sort field. Allowed values: "
                "reserved_at, status, session"
            ),
        )

    if sort_order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sort order must be 'asc' or 'desc'",
        )

    # ========================================================
    # EXPIRE OLD RESERVATIONS
    # ========================================================

    expire_old_reservations(db)

    # ========================================================
    # BASE QUERY
    # ========================================================

    query = (
        db.query(
            Registration,
            EventSession,
            Event,
        )
        .join(
            EventSession,
            Registration.session_id == EventSession.id,
        )
        .join(
            Event,
            EventSession.event_id == Event.id,
        )
    )

    # ========================================================
    # VISIBILITY
    # ========================================================

    viewer_role = getattr(viewer, "role", None)

    # --------------------------------------------------------
    # ORGANIZER
    # --------------------------------------------------------

    if viewer_role == "organizer":
        query = query.filter(
            Event.organizer_id == viewer.id
        )

    # --------------------------------------------------------
    # CHECK-IN STAFF
    # --------------------------------------------------------

    elif viewer_role == "checkin_staff":
        query = query.join(
            SessionStaff,
            SessionStaff.session_id == EventSession.id,
        ).filter(
            SessionStaff.staff_id == viewer.id
        )

    # --------------------------------------------------------
    # INVALID ROLE
    # --------------------------------------------------------

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only organizers and check-in staff "
                "can search registrations"
            ),
        )

    # ========================================================
    # TEXT SEARCH
    # ========================================================

    if search:
        search_term = f"%{search.strip()}%"

        query = query.filter(
            or_(
                Registration.attendee_name.ilike(
                    search_term
                ),
                Registration.attendee_email.ilike(
                    search_term
                ),
            )
        )

    # ========================================================
    # EVENT FILTER
    # ========================================================

    if event_id is not None:
        query = query.filter(
            Event.id == event_id
        )

    # ========================================================
    # SESSION FILTER
    # ========================================================

    if session_id is not None:
        query = query.filter(
            EventSession.id == session_id
        )

    # ========================================================
    # STATUS FILTER
    # ========================================================

    if registration_status is not None:
        query = query.filter(
            Registration.status == registration_status
        )

    # ========================================================
    # TOTAL MATCHES
    # ========================================================

    total = query.count()

    # ========================================================
    # SORTING
    # ========================================================

    sort_column = allowed_sort_fields[sort_by]

    if sort_order == "asc":
        query = query.order_by(
            asc(sort_column),
            asc(Registration.id),
        )
    else:
        query = query.order_by(
            desc(sort_column),
            desc(Registration.id),
        )

    # ========================================================
    # PAGINATION
    # ========================================================

    offset = (page - 1) * page_size

    rows = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # ========================================================
    # TOTAL PAGES
    # ========================================================

    total_pages = (
        (total + page_size - 1) // page_size
        if total > 0
        else 0
    )

    # ========================================================
    # BUILD RESPONSE
    # ========================================================

    items = []

    for registration, event_session, event in rows:
        items.append(
            {
                "id": registration.id,
                "user_id": registration.user_id,
                "session_id": event_session.id,
                "session_title": event_session.title,
                "event_id": event.id,
                "event_title": event.title,
                "attendee_name": registration.attendee_name,
                "attendee_email": registration.attendee_email,
                "status": registration.status,
                "reserved_at": registration.reserved_at,
                "confirmed_at": registration.confirmed_at,
                "checked_in_at": registration.checked_in_at,
                "cancelled_at": registration.cancelled_at,
                "expired_at": registration.expired_at,
            }
        )

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ============================================================
# CANCEL REGISTRATION
# ============================================================

def cancel_registration(
    db: Session,
    registration_id: int,
    actor_user_id: int,
) -> Registration:
    """
    Cancel a Reserved or Confirmed registration.

    Goal 9:
        Creates a cancellation history entry.
    """

    expire_old_reservations(db)

    registration = (
        db.query(Registration)
        .filter(
            Registration.id == registration_id,
        )
        .first()
    )

    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )

    event_session = (
        db.query(EventSession)
        .filter(
            EventSession.id == registration.session_id,
        )
        .first()
    )

    if event_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    event = (
        db.query(Event)
        .filter(
            Event.id == event_session.event_id,
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    # ========================================================
    # PERMISSION
    # ========================================================

    if (
        registration.user_id != actor_user_id
        and event.organizer_id != actor_user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to cancel this registration"
            ),
        )

    # ========================================================
    # VALIDATE TRANSITION
    # ========================================================

    if registration.status == "checked_in":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Checked-in registrations "
                "cannot be cancelled"
            ),
        )

    if registration.status == "expired":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Expired registrations "
                "cannot be cancelled"
            ),
        )

    if registration.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration is already cancelled",
        )

    if registration.status not in {
        "reserved",
        "confirmed",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Registration cannot be cancelled "
                f"from status '{registration.status}'"
            ),
        )

    # ========================================================
    # CANCEL
    # ========================================================

    old_status = registration.status
    now = datetime.utcnow()

    registration.status = "cancelled"
    registration.cancelled_at = now

    # --------------------------------------------------------
    # GOAL 9 — REGISTRATION HISTORY
    # --------------------------------------------------------

    create_history_entry(
        db=db,
        registration_id=registration.id,
        action="cancelled",
        actor_user_id=actor_user_id,
        old_status=old_status,
        new_status="cancelled",
        note="Registration cancelled",
    )

    # Commit registration + history together.
    db.commit()

    db.refresh(registration)

    # ========================================================
    # UPDATE CAPACITY ALERT
    # ========================================================

    update_capacity_alert(
        db=db,
        session_id=registration.session_id,
    )

    return registration


# ============================================================
# CONFIRM REGISTRATION
# ============================================================

def confirm_registration(
    db: Session,
    registration_id: int,
    actor_user_id: int,
) -> Registration:
    """
    Reserved → Confirmed

    Only the organizer who owns the event can confirm
    a registration.

    Goal 9:
        Creates a confirmation history entry.
    """

    expire_old_reservations(db)

    registration = (
        db.query(Registration)
        .filter(
            Registration.id == registration_id,
        )
        .first()
    )

    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )

    event_session = (
        db.query(EventSession)
        .filter(
            EventSession.id == registration.session_id,
        )
        .first()
    )

    if event_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    event = (
        db.query(Event)
        .filter(
            Event.id == event_session.event_id,
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    # ========================================================
    # OWNERSHIP
    # ========================================================

    if event.organizer_id != actor_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only confirm registrations "
                "for your own events"
            ),
        )

    # ========================================================
    # VALIDATE TRANSITION
    # ========================================================

    if registration.status == "expired":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Expired registrations "
                "cannot be confirmed"
            ),
        )

    if registration.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cancelled registrations "
                "cannot be confirmed"
            ),
        )

    if registration.status == "confirmed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration is already confirmed",
        )

    if registration.status == "checked_in":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Registration is already checked in"
            ),
        )

    if registration.status != "reserved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Registration cannot be confirmed "
                f"from status '{registration.status}'"
            ),
        )

    # ========================================================
    # CONFIRM
    # ========================================================

    old_status = registration.status
    now = datetime.utcnow()

    registration.status = "confirmed"
    registration.confirmed_at = now

    # --------------------------------------------------------
    # GOAL 9 — REGISTRATION HISTORY
    # --------------------------------------------------------

    create_history_entry(
        db=db,
        registration_id=registration.id,
        action="confirmed",
        actor_user_id=actor_user_id,
        old_status=old_status,
        new_status="confirmed",
        note="Registration confirmed by organizer",
    )

    # Commit registration + history together.
    db.commit()

    db.refresh(registration)

    # ========================================================
    # UPDATE CAPACITY ALERT
    # ========================================================

    update_capacity_alert(
        db=db,
        session_id=registration.session_id,
    )

    return registration


# ============================================================
# CHECK IN REGISTRATION
# ============================================================

def check_in_registration(
    db: Session,
    registration_id: int,
    actor_user_id: int,
) -> Registration:
    """
    Confirmed → Checked In

    Allowed actors:

        1. Organizer who owns the event
        2. Check-in staff assigned to the session

    Registration lifecycle:

        Reserved
            ↓
        Confirmed
            ↓
        Checked In

    Goal 9:
        Creates a check-in history entry.
    """

    # --------------------------------------------------------
    # Expire old reservations
    # --------------------------------------------------------

    expire_old_reservations(db)

    # --------------------------------------------------------
    # Find registration
    # --------------------------------------------------------

    registration = (
        db.query(Registration)
        .filter(
            Registration.id == registration_id,
        )
        .first()
    )

    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )

    # --------------------------------------------------------
    # Find session
    # --------------------------------------------------------

    event_session = (
        db.query(EventSession)
        .filter(
            EventSession.id == registration.session_id,
        )
        .first()
    )

    if event_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # --------------------------------------------------------
    # Find parent event
    # --------------------------------------------------------

    event = (
        db.query(Event)
        .filter(
            Event.id == event_session.event_id,
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    # ========================================================
    # PERMISSION
    # ========================================================

    # --------------------------------------------------------
    # Check whether actor is event organizer
    # --------------------------------------------------------

    is_organizer = (
        event.organizer_id == actor_user_id
    )

    # --------------------------------------------------------
    # Check whether actor is assigned check-in staff
    # --------------------------------------------------------

    is_assigned_staff = (
        db.query(SessionStaff)
        .filter(
            SessionStaff.session_id == event_session.id,
            SessionStaff.staff_id == actor_user_id,
        )
        .first()
        is not None
    )

    # --------------------------------------------------------
    # Allow organizer OR assigned check-in staff
    # --------------------------------------------------------

    if not is_organizer and not is_assigned_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only check in registrations "
                "for your own events or sessions assigned "
                "to you"
            ),
        )

    # ========================================================
    # VALIDATE REGISTRATION TRANSITION
    # ========================================================

    # --------------------------------------------------------
    # Reserved cannot directly check in
    # --------------------------------------------------------

    if registration.status == "reserved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Reserved registrations must be confirmed "
                "before check-in"
            ),
        )

    # --------------------------------------------------------
    # Cancelled cannot check in
    # --------------------------------------------------------

    if registration.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cancelled registrations "
                "cannot be checked in"
            ),
        )

    # --------------------------------------------------------
    # Expired cannot check in
    # --------------------------------------------------------

    if registration.status == "expired":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Expired registrations "
                "cannot be checked in"
            ),
        )

    # --------------------------------------------------------
    # Already checked in
    # --------------------------------------------------------

    if registration.status == "checked_in":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration is already checked in",
        )

    # --------------------------------------------------------
    # Only confirmed can be checked in
    # --------------------------------------------------------

    if registration.status != "confirmed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Registration cannot be checked in "
                f"from status '{registration.status}'"
            ),
        )

    # ========================================================
    # CHECK IN
    # ========================================================

    old_status = registration.status
    now = datetime.utcnow()

    registration.status = "checked_in"
    registration.checked_in_at = now

    # --------------------------------------------------------
    # GOAL 9 — REGISTRATION HISTORY
    # --------------------------------------------------------

    create_history_entry(
        db=db,
        registration_id=registration.id,
        action="checked_in",
        actor_user_id=actor_user_id,
        old_status=old_status,
        new_status="checked_in",
        note="Registration checked in",
    )

    # Commit registration + history together.
    db.commit()

    db.refresh(registration)

    # ========================================================
    # GOAL 10 — UPDATE CAPACITY ALERT
    # ========================================================

    update_capacity_alert(
        db=db,
        session_id=registration.session_id,
    )

    return registration


# ============================================================
# MANUAL EXPIRATION
# ============================================================

def expire_registration(
    db: Session,
    registration_id: int,
) -> Registration:
    """
    Manually expire a Reserved registration.

    Goal 9:
        Creates an expiration history entry.
    """

    registration = (
        db.query(Registration)
        .filter(
            Registration.id == registration_id,
        )
        .first()
    )

    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )

    if registration.status != "reserved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only reserved registrations "
                "can expire"
            ),
        )

    expiration_time = (
        registration.reserved_at
        + timedelta(minutes=HOLDING_WINDOW_MINUTES)
    )

    now = datetime.utcnow()

    if now < expiration_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Registration has not reached "
                "its expiration time"
            ),
        )

    # ========================================================
    # EXPIRE
    # ========================================================

    old_status = registration.status

    registration.status = "expired"
    registration.expired_at = now

    # --------------------------------------------------------
    # GOAL 9 — REGISTRATION HISTORY
    # --------------------------------------------------------

    create_history_entry(
        db=db,
        registration_id=registration.id,
        action="expired",
        actor_user_id=None,
        old_status=old_status,
        new_status="expired",
        note="Registration manually expired",
    )

    # Commit registration + history together.
    db.commit()

    db.refresh(registration)

    # ========================================================
    # UPDATE CAPACITY ALERT
    # ========================================================

    update_capacity_alert(
        db=db,
        session_id=registration.session_id,
    )

    return registration


# ============================================================
# SESSION REGISTRATIONS
# ============================================================

def get_session_registrations(
    db: Session,
    session_id: int,
    organizer_id: int,
) -> list[Registration]:
    """
    Return all registrations for a session.

    Only the organizer who owns the parent event
    can access this list.
    """

    expire_old_reservations(db)

    event_session = (
        db.query(EventSession)
        .filter(
            EventSession.id == session_id,
        )
        .first()
    )

    if event_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    event = (
        db.query(Event)
        .filter(
            Event.id == event_session.event_id,
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    if event.organizer_id != organizer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only view registrations "
                "for your own sessions"
            ),
        )

    return (
        db.query(Registration)
        .filter(
            Registration.session_id == session_id,
        )
        .order_by(
            Registration.reserved_at.desc()
        )
        .all()
    )


# ============================================================
# SESSION STATISTICS
# ============================================================

def get_session_stats(
    db: Session,
    session_id: int,
    organizer_id: int,
) -> dict:
    """
    Return registration statistics for a session.
    """

    expire_old_reservations(db)

    event_session = (
        db.query(EventSession)
        .filter(
            EventSession.id == session_id,
        )
        .first()
    )

    if event_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    event = (
        db.query(Event)
        .filter(
            Event.id == event_session.event_id,
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    if event.organizer_id != organizer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only view statistics "
                "for your own sessions"
            ),
        )

    def count_status(
        registration_status: str,
    ) -> int:
        return (
            db.query(func.count(Registration.id))
            .filter(
                Registration.session_id == session_id,
                Registration.status == registration_status,
            )
            .scalar()
            or 0
        )

    reserved = count_status("reserved")
    confirmed = count_status("confirmed")
    checked_in = count_status("checked_in")
    cancelled = count_status("cancelled")
    expired = count_status("expired")

    active_registrations = (
        reserved
        + confirmed
        + checked_in
    )

    available_seats = max(
        event_session.capacity
        - active_registrations,
        0,
    )

    return {
        "session_id": event_session.id,
        "session_title": event_session.title,
        "capacity": event_session.capacity,
        "reserved": reserved,
        "confirmed": confirmed,
        "checked_in": checked_in,
        "cancelled": cancelled,
        "expired": expired,
        "active_registrations": active_registrations,
        "available_seats": available_seats,
    }


# ============================================================
# REGISTRATION STATUS FOR CURRENT USER
# ============================================================

def get_registration_status(
    db: Session,
    session_id: int,
    user_id: int,
) -> dict:
    """
    Return the current user's registration status
    for a particular session.
    """

    expire_old_reservations(db)

    event_session = (
        db.query(EventSession)
        .filter(
            EventSession.id == session_id,
        )
        .first()
    )

    if event_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # --------------------------------------------------------
    # Count active registrations
    # --------------------------------------------------------

    active_registrations = (
        db.query(func.count(Registration.id))
        .filter(
            Registration.session_id == session_id,
            Registration.status.in_(ACTIVE_STATUSES),
        )
        .scalar()
        or 0
    )

    available_seats = max(
        event_session.capacity
        - active_registrations,
        0,
    )

    # --------------------------------------------------------
    # Find user's latest registration
    # --------------------------------------------------------

    registration = (
        db.query(Registration)
        .filter(
            Registration.session_id == session_id,
            Registration.user_id == user_id,
        )
        .order_by(
            Registration.id.desc()
        )
        .first()
    )

    if registration is None:
        registration_status = "not_registered"
    else:
        registration_status = registration.status

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "session_id": event_session.id,
        "capacity": event_session.capacity,
        "available_seats": available_seats,
        "registration_status": registration_status,
    }


# ============================================================
# BULK CSV IMPORT
# ============================================================

def bulk_import_registrations(
    db: Session,
    session_id: int,
    organizer_id: int,
    csv_content: str,
) -> dict:
    """
    Import registrations from CSV.

    Expected CSV columns:

        attendee_name,attendee_email

    Each row is independently processed.

    Goal 9:
        Every successfully created registration gets
        a registration history entry.
    """

    # --------------------------------------------------------
    # Find session
    # --------------------------------------------------------

    event_session = (
        db.query(EventSession)
        .filter(
            EventSession.id == session_id,
        )
        .first()
    )

    if event_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # --------------------------------------------------------
    # Find event
    # --------------------------------------------------------

    event = (
        db.query(Event)
        .filter(
            Event.id == event_session.event_id,
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    # --------------------------------------------------------
    # Organizer permission
    # --------------------------------------------------------

    if event.organizer_id != organizer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only import registrations "
                "for your own sessions"
            ),
        )

    # --------------------------------------------------------
    # Event validation
    # --------------------------------------------------------

    if event.is_archived:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cannot import registrations "
                "into an archived event"
            ),
        )

    # --------------------------------------------------------
    # Parse CSV
    # --------------------------------------------------------

    try:
        csv_file = io.StringIO(
            csv_content,
            newline="",
        )

        reader = csv.DictReader(csv_file)

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid CSV file: {exc}",
        )

    # --------------------------------------------------------
    # Validate headers
    # --------------------------------------------------------

    if reader.fieldnames is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file is empty or missing headers",
        )

    required_columns = {
        "attendee_name",
        "attendee_email",
    }

    actual_columns = {
        column.strip()
        for column in reader.fieldnames
        if column
    }

    missing_columns = (
        required_columns - actual_columns
    )

    if missing_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "CSV is missing required columns: "
                + ", ".join(sorted(missing_columns))
            ),
        )

    # --------------------------------------------------------
    # Expire old reservations
    # --------------------------------------------------------

    expire_old_reservations(db)

    # --------------------------------------------------------
    # Lock session
    # --------------------------------------------------------

    event_session = (
        db.query(EventSession)
        .filter(
            EventSession.id == session_id,
        )
        .with_for_update()
        .first()
    )

    if event_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # --------------------------------------------------------
    # Existing active emails
    # --------------------------------------------------------

    existing_emails = {
        email[0].lower()
        for email in (
            db.query(Registration.attendee_email)
            .filter(
                Registration.session_id == session_id,
                Registration.status.in_(ACTIVE_STATUSES),
            )
            .all()
        )
        if email[0]
    }

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    results = []

    created = 0
    duplicates = 0
    rejected = 0

    # --------------------------------------------------------
    # Process rows
    # --------------------------------------------------------

    for row_number, row in enumerate(
        reader,
        start=2,
    ):

        attendee_name = (
            row.get("attendee_name") or ""
        ).strip()

        attendee_email = (
            row.get("attendee_email") or ""
        ).strip().lower()

        # ----------------------------------------------------
        # Validate name
        # ----------------------------------------------------

        if not attendee_name:
            rejected += 1

            results.append(
                {
                    "row_number": row_number,
                    "attendee_name": None,
                    "attendee_email": (
                        attendee_email or None
                    ),
                    "result": "rejected",
                    "reason": "Attendee name is required",
                    "registration_id": None,
                }
            )

            continue

        if len(attendee_name) > 100:
            rejected += 1

            results.append(
                {
                    "row_number": row_number,
                    "attendee_name": attendee_name,
                    "attendee_email": (
                        attendee_email or None
                    ),
                    "result": "rejected",
                    "reason": (
                        "Attendee name cannot exceed "
                        "100 characters"
                    ),
                    "registration_id": None,
                }
            )

            continue

        # ----------------------------------------------------
        # Validate email
        # ----------------------------------------------------

        try:
            from pydantic import TypeAdapter, EmailStr

            validated_email = TypeAdapter(
                EmailStr
            ).validate_python(attendee_email)

            attendee_email = str(
                validated_email
            ).lower()

        except Exception:
            rejected += 1

            results.append(
                {
                    "row_number": row_number,
                    "attendee_name": attendee_name,
                    "attendee_email": (
                        attendee_email or None
                    ),
                    "result": "rejected",
                    "reason": "Invalid email address",
                    "registration_id": None,
                }
            )

            continue

        # ----------------------------------------------------
        # Duplicate check
        # ----------------------------------------------------

        if attendee_email in existing_emails:
            duplicates += 1

            results.append(
                {
                    "row_number": row_number,
                    "attendee_name": attendee_name,
                    "attendee_email": attendee_email,
                    "result": "duplicate",
                    "reason": (
                        "Email is already registered "
                        "for this session"
                    ),
                    "registration_id": None,
                }
            )

            continue

        # ----------------------------------------------------
        # Capacity check
        # ----------------------------------------------------

        active_count = (
            db.query(func.count(Registration.id))
            .filter(
                Registration.session_id == session_id,
                Registration.status.in_(ACTIVE_STATUSES),
            )
            .scalar()
            or 0
        )

        if active_count >= event_session.capacity:
            rejected += 1

            results.append(
                {
                    "row_number": row_number,
                    "attendee_name": attendee_name,
                    "attendee_email": attendee_email,
                    "result": "rejected",
                    "reason": "Session capacity is full",
                    "registration_id": None,
                }
            )

            continue

        # ----------------------------------------------------
        # Create reservation
        # ----------------------------------------------------

        now = datetime.utcnow()

        registration = Registration(
            user_id=None,
            session_id=session_id,
            attendee_name=attendee_name,
            attendee_email=attendee_email,
            status="reserved",
            reserved_at=now,
        )

        db.add(registration)

        # Flush so registration.id becomes available.
        db.flush()

        # ----------------------------------------------------
        # GOAL 9 — REGISTRATION HISTORY
        # ----------------------------------------------------

        create_history_entry(
            db=db,
            registration_id=registration.id,
            action="reserved",
            actor_user_id=organizer_id,
            old_status=None,
            new_status="reserved",
            note="Registration created through bulk CSV import",
        )

        # Keep local set updated so duplicate rows inside
        # the same CSV are detected.
        existing_emails.add(
            attendee_email
        )

        created += 1

        results.append(
            {
                "row_number": row_number,
                "attendee_name": attendee_name,
                "attendee_email": attendee_email,
                "result": "created",
                "reason": None,
                "registration_id": registration.id,
            }
        )

    # --------------------------------------------------------
    # Commit all successful rows + history entries
    # --------------------------------------------------------

    db.commit()

    # --------------------------------------------------------
    # UPDATE CAPACITY ALERT
    # --------------------------------------------------------

    if created > 0:
        update_capacity_alert(
            db=db,
            session_id=session_id,
        )

    return {
        "session_id": session_id,
        "total_rows": (
            created
            + duplicates
            + rejected
        ),
        "created": created,
        "duplicates": duplicates,
        "rejected": rejected,
        "rows": results,
    }


# ============================================================
# EXPORT SESSION REGISTRATIONS
# ============================================================

def export_session_registrations(
    db: Session,
    session_id: int,
    organizer_id: int,
) -> str:
    """
    Export all registrations for a session as CSV.

    Only the organizer who owns the event can export.
    """

    # --------------------------------------------------------
    # Find session
    # --------------------------------------------------------

    event_session = (
        db.query(EventSession)
        .filter(
            EventSession.id == session_id,
        )
        .first()
    )

    if event_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # --------------------------------------------------------
    # Find event
    # --------------------------------------------------------

    event = (
        db.query(Event)
        .filter(
            Event.id == event_session.event_id,
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    # --------------------------------------------------------
    # Permission
    # --------------------------------------------------------

    if event.organizer_id != organizer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only export registrations "
                "for your own sessions"
            ),
        )

    # --------------------------------------------------------
    # Expire old reservations
    # --------------------------------------------------------

    expire_old_reservations(db)

    # --------------------------------------------------------
    # Get registrations
    # --------------------------------------------------------

    registrations = (
        db.query(Registration)
        .filter(
            Registration.session_id == session_id,
        )
        .order_by(
            Registration.reserved_at.asc(),
            Registration.id.asc(),
        )
        .all()
    )

    # --------------------------------------------------------
    # Create CSV
    # --------------------------------------------------------

    output = io.StringIO(
        newline="",
    )

    writer = csv.writer(output)

    writer.writerow(
        [
            "registration_id",
            "attendee_name",
            "attendee_email",
            "status",
            "reserved_at",
            "confirmed_at",
            "checked_in_at",
            "cancelled_at",
            "expired_at",
        ]
    )

    for registration in registrations:
        writer.writerow(
            [
                registration.id,
                registration.attendee_name,
                registration.attendee_email,
                registration.status,
                (
                    registration.reserved_at.isoformat()
                    if registration.reserved_at
                    else ""
                ),
                (
                    registration.confirmed_at.isoformat()
                    if registration.confirmed_at
                    else ""
                ),
                (
                    registration.checked_in_at.isoformat()
                    if registration.checked_in_at
                    else ""
                ),
                (
                    registration.cancelled_at.isoformat()
                    if registration.cancelled_at
                    else ""
                ),
                (
                    registration.expired_at.isoformat()
                    if registration.expired_at
                    else ""
                ),
            ]
        )

    return output.getvalue()


# ============================================================
# GET REGISTRATION HISTORY
# ============================================================

def get_registration_history(
    db: Session,
    registration_id: int,
):
    """
    Return the complete immutable history timeline
    for a registration.

    History is returned oldest first so that the
    registration lifecycle can be followed chronologically.

    The actual validation and history retrieval logic is
    delegated to registration_history_service.
    """

    registration = (
        db.query(Registration)
        .filter(
            Registration.id == registration_id,
        )
        .first()
    )

    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )

    return (
        db.query(RegistrationHistory)
        .filter(
            RegistrationHistory.registration_id
            == registration_id
        )
        .order_by(
            RegistrationHistory.created_at.asc(),
            RegistrationHistory.id.asc(),
        )
        .all()
    )