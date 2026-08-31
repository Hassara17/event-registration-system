from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session as DBSession

from app.models.event import Event
from app.models.registration import Registration
from app.models.session import Session
from app.schemas.session import SessionCreate, SessionUpdate


def create_session(
    db: DBSession,
    event_id: int,
    session_data: SessionCreate,
) -> Session:
    # 1. Check that the event exists
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

    # 2. Check that the session fits inside the event
    session_end = (
        session_data.start_time
        + __import__("datetime").timedelta(
            minutes=session_data.duration
        )
    )

    if session_data.start_time < event.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session cannot start before the event starts",
        )

    if session_end > event.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session cannot end after the event ends",
        )

    # 3. Create session
    session = Session(
        event_id=event_id,
        title=session_data.title,
        start_time=session_data.start_time,
        duration=session_data.duration,
        location=session_data.location,
        capacity=session_data.capacity,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def get_session(
    db: DBSession,
    session_id: int,
) -> Session | None:
    return (
        db.query(Session)
        .filter(Session.id == session_id)
        .first()
    )


def get_event_sessions(
    db: DBSession,
    event_id: int,
) -> list[Session]:
    # Check event exists
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

    return (
        db.query(Session)
        .filter(Session.event_id == event_id)
        .order_by(Session.start_time.asc())
        .all()
    )


def update_session(
    db: DBSession,
    session: Session,
    session_data: SessionUpdate,
) -> Session:
    update_data = session_data.model_dump(
        exclude_unset=True
    )

    # --------------------------------------------------
    # Capacity validation
    # --------------------------------------------------

    if "capacity" in update_data:
        new_capacity = update_data["capacity"]

        active_registrations = (
            db.query(func.count(Registration.id))
            .filter(
                Registration.session_id == session.id,
                Registration.status.in_(
                    [
                        "reserved",
                        "confirmed",
                        "checked_in",
                    ]
                ),
            )
            .scalar()
        )

        if new_capacity < active_registrations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Capacity cannot be less than the "
                    f"number of active registrations "
                    f"({active_registrations})"
                ),
            )

    # --------------------------------------------------
    # Validate updated timing
    # --------------------------------------------------

    start_time = update_data.get(
        "start_time",
        session.start_time,
    )

    duration = update_data.get(
        "duration",
        session.duration,
    )

    session_end = (
        start_time
        + __import__("datetime").timedelta(
            minutes=duration
        )
    )

    event = (
        db.query(Event)
        .filter(Event.id == session.event_id)
        .first()
    )

    if event is not None:
        if start_time < event.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Session cannot start before "
                    "the event starts"
                ),
            )

        if session_end > event.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Session cannot end after "
                    "the event ends"
                ),
            )

    # --------------------------------------------------
    # Apply updates
    # --------------------------------------------------

    for field, value in update_data.items():
        setattr(session, field, value)

    db.commit()
    db.refresh(session)

    return session


def delete_session(
    db: DBSession,
    session: Session,
) -> None:
    # Do not delete a session that has registrations
    registration_count = (
        db.query(func.count(Registration.id))
        .filter(
            Registration.session_id == session.id
        )
        .scalar()
    )

    if registration_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Cannot delete a session that has "
                "registrations"
            ),
        )

    db.delete(session)
    db.commit()Q