from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_user,
    get_db,
    require_role,
)
from app.models.event import Event
from app.models.registration import Registration
from app.models.session import Session as EventSession
from app.models.user import User


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)


# ============================================================
# CONSTANTS
# ============================================================

ACTIVE_STATUSES = {
    "reserved",
    "confirmed",
    "checked_in",
}

INDIA_TIMEZONE = ZoneInfo("Asia/Kolkata")


# ============================================================
# DATETIME HELPERS
# ============================================================

def make_utc_aware(value: datetime) -> datetime:
    """
    Convert any datetime into a timezone-aware UTC datetime.

    Rules:

    1. If the datetime already has timezone information,
       convert it directly to UTC.

    2. If the datetime is naive, treat it as Asia/Kolkata
       local time and convert it to UTC.

    This is important because existing database records may
    contain naive timestamps while FastAPI may receive
    timezone-aware timestamps such as:

        2026-08-01T05:30:00Z

    which means:

        2026-08-01 11:00 AM IST
    """

    if value.tzinfo is None:
        value = value.replace(
            tzinfo=INDIA_TIMEZONE
        )

    return value.astimezone(timezone.utc)


def utc_to_india_naive(value: datetime) -> datetime:
    """
    Convert a datetime to Asia/Kolkata and remove timezone
    information before storing it in a naive database column.

    Example:

        2026-08-01T05:30:00Z
                ↓
        2026-08-01 11:00:00

    The database therefore stores local IST time.
    """

    utc_value = make_utc_aware(value)

    india_value = utc_value.astimezone(
        INDIA_TIMEZONE
    )

    return india_value.replace(
        tzinfo=None
    )


# ============================================================
# CREATE SESSION
# ============================================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
def create_session(
    event_id: int,
    title: str,
    start_time: datetime,
    duration: int,
    location: str,
    capacity: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):
    # --------------------------------------------------------
    # 1. Check event exists
    # --------------------------------------------------------

    event = (
        db.query(Event)
        .filter(Event.id == event_id)
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    # --------------------------------------------------------
    # 2. Check organizer owns event
    # --------------------------------------------------------

    if event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only create sessions "
                "for your own events"
            ),
        )

    # --------------------------------------------------------
    # 3. Validate title
    # --------------------------------------------------------

    if not title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session title cannot be empty",
        )

    # --------------------------------------------------------
    # 4. Validate duration
    # --------------------------------------------------------

    if duration <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Session duration must be "
                "greater than zero"
            ),
        )

    # --------------------------------------------------------
    # 5. Validate capacity
    # --------------------------------------------------------

    if capacity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Session capacity must be "
                "greater than zero"
            ),
        )

    # --------------------------------------------------------
    # 6. Normalize datetimes
    # --------------------------------------------------------

    start_time_utc = make_utc_aware(
        start_time
    )

    event_start_utc = make_utc_aware(
        event.start_date
    )

    event_end_utc = make_utc_aware(
        event.end_date
    )

    # --------------------------------------------------------
    # 7. Validate session starts inside event
    # --------------------------------------------------------

    if start_time_utc < event_start_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Session cannot start before "
                "the event starts"
            ),
        )

    # --------------------------------------------------------
    # 8. Validate session ends inside event
    # --------------------------------------------------------

    session_end_utc = (
        start_time_utc.timestamp()
        + (duration * 60)
    )

    event_end_timestamp = (
        event_end_utc.timestamp()
    )

    if session_end_utc > event_end_timestamp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Session cannot end after "
                "the event ends"
            ),
        )

    # --------------------------------------------------------
    # 9. Convert session time to IST for database
    # --------------------------------------------------------

    start_time_ist = utc_to_india_naive(
        start_time
    )

    # --------------------------------------------------------
    # 10. Create session
    # --------------------------------------------------------

    event_session = EventSession(
        event_id=event_id,
        title=title.strip(),
        start_time=start_time_ist,
        duration=duration,
        location=location.strip(),
        capacity=capacity,
    )

    db.add(event_session)

    # --------------------------------------------------------
    # 11. Save
    # --------------------------------------------------------

    db.commit()

    db.refresh(event_session)

    return event_session


# ============================================================
# GET SINGLE SESSION
# ============================================================

@router.get(
    "/{session_id}",
)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
):
    session = (
        db.query(EventSession)
        .filter(
            EventSession.id == session_id
        )
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    return session


# ============================================================
# GET ALL SESSIONS FOR AN EVENT
# ============================================================

@router.get(
    "/event/{event_id}",
)
def get_event_sessions(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    # --------------------------------------------------------
    # 1. Check event exists
    # --------------------------------------------------------

    event = (
        db.query(Event)
        .filter(Event.id == event_id)
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    # --------------------------------------------------------
    # 2. Get sessions
    # --------------------------------------------------------

    sessions = (
        db.query(EventSession)
        .filter(
            EventSession.event_id == event_id
        )
        .order_by(
            EventSession.start_time.asc()
        )
        .all()
    )

    return sessions


# ============================================================
# UPDATE SESSION
# ============================================================

@router.patch(
    "/{session_id}",
)
def update_session(
    session_id: int,
    title: str | None = None,
    start_time: datetime | None = None,
    duration: int | None = None,
    location: str | None = None,
    capacity: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):
    # --------------------------------------------------------
    # 1. Get session
    # --------------------------------------------------------

    session = (
        db.query(EventSession)
        .filter(
            EventSession.id == session_id
        )
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # --------------------------------------------------------
    # 2. Get parent event
    # --------------------------------------------------------

    event = (
        db.query(Event)
        .filter(
            Event.id == session.event_id
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    # --------------------------------------------------------
    # 3. Check ownership
    # --------------------------------------------------------

    if event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only modify "
                "your own sessions"
            ),
        )

    # --------------------------------------------------------
    # 4. Validate title
    # --------------------------------------------------------

    if title is not None:

        if not title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session title cannot be empty",
            )

    # --------------------------------------------------------
    # 5. Validate duration
    # --------------------------------------------------------

    if duration is not None:

        if duration <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Session duration must be "
                    "greater than zero"
                ),
            )

    # --------------------------------------------------------
    # 6. Validate capacity
    # --------------------------------------------------------

    if capacity is not None:

        if capacity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Session capacity must be "
                    "greater than zero"
                ),
            )

        active_count = (
            db.query(
                func.count(Registration.id)
            )
            .filter(
                Registration.session_id
                == session_id,

                Registration.status.in_(
                    ACTIVE_STATUSES
                ),
            )
            .scalar()
        )

        if capacity < active_count:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Capacity cannot be less than "
                    "the number of active registrations "
                    f"({active_count})"
                ),
            )

    # --------------------------------------------------------
    # 7. Calculate final values
    # --------------------------------------------------------

    if start_time is not None:
        final_start_time = start_time
    else:
        final_start_time = session.start_time

    if duration is not None:
        final_duration = duration
    else:
        final_duration = session.duration

    # --------------------------------------------------------
    # 8. Normalize datetimes
    # --------------------------------------------------------

    final_start_time_utc = make_utc_aware(
        final_start_time
    )

    event_start_utc = make_utc_aware(
        event.start_date
    )

    event_end_utc = make_utc_aware(
        event.end_date
    )

    # --------------------------------------------------------
    # 9. Validate session starts inside event
    # --------------------------------------------------------

    if final_start_time_utc < event_start_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Session cannot start before "
                "the event starts"
            ),
        )

    # --------------------------------------------------------
    # 10. Validate session end time
    # --------------------------------------------------------

    session_end_timestamp = (
        final_start_time_utc.timestamp()
        + (final_duration * 60)
    )

    event_end_timestamp = (
        event_end_utc.timestamp()
    )

    if session_end_timestamp > event_end_timestamp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Session cannot end after "
                "the event ends"
            ),
        )

    # --------------------------------------------------------
    # 11. Apply updates
    # --------------------------------------------------------

    if title is not None:
        session.title = title.strip()

    if start_time is not None:

        session.start_time = (
            utc_to_india_naive(
                final_start_time
            )
        )

    if duration is not None:
        session.duration = duration

    if location is not None:
        session.location = location.strip()

    if capacity is not None:
        session.capacity = capacity

    # --------------------------------------------------------
    # 12. Save
    # --------------------------------------------------------

    db.commit()

    db.refresh(session)

    return session


# ============================================================
# DELETE SESSION
# ============================================================

@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):
    # --------------------------------------------------------
    # 1. Get session
    # --------------------------------------------------------

    session = (
        db.query(EventSession)
        .filter(
            EventSession.id == session_id
        )
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # --------------------------------------------------------
    # 2. Get parent event
    # --------------------------------------------------------

    event = (
        db.query(Event)
        .filter(
            Event.id == session.event_id
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    # --------------------------------------------------------
    # 3. Check ownership
    # --------------------------------------------------------

    if event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only delete "
                "your own sessions"
            ),
        )

    # --------------------------------------------------------
    # 4. Check active registrations
    # --------------------------------------------------------

    active_count = (
        db.query(
            func.count(Registration.id)
        )
        .filter(
            Registration.session_id
            == session_id,

            Registration.status.in_(
                ACTIVE_STATUSES
            ),
        )
        .scalar()
    )

    if active_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cannot delete a session with "
                f"{active_count} active registration(s)"
            ),
        )

    # --------------------------------------------------------
    # 5. Delete session
    # --------------------------------------------------------

    db.delete(session)

    db.commit()

    return None