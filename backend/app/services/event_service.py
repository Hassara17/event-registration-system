from datetime import date, datetime, time, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.registration import Registration
from app.models.session import Session as EventSession
from app.schemas.event import EventCreate, EventUpdate


ACTIVE_STATUSES = {
    "reserved",
    "confirmed",
    "checked_in",
}


# ============================================================
# CREATE EVENT
# ============================================================

def create_event(
    db: Session,
    event_data: EventCreate,
    organizer_id: int,
) -> Event:

    event = Event(
        title=event_data.title.strip(),
        description=event_data.description,
        venue=event_data.venue.strip(),
        start_date=event_data.start_date,
        end_date=event_data.end_date,
        capacity=event_data.capacity,
        is_published=event_data.is_published,
        is_archived=False,
        organizer_id=organizer_id,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


# ============================================================
# GET SINGLE EVENT
# ============================================================

def get_event(
    db: Session,
    event_id: int,
) -> Event | None:

    statement = select(Event).where(
        Event.id == event_id
    )

    return db.scalar(statement)


# ============================================================
# GET EVENTS
# ============================================================

def get_events(
    db: Session,
    search: str | None = None,
    venue: str | None = None,
    event_date: date | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "start_date",
    sort_order: str = "asc",
    archived: bool = False,
) -> list[Event]:
    """
    Return events filtered by archive status.

    archived=False:
        Return active events.

    archived=True:
        Return archived events.
    """

    # --------------------------------------------------------
    # Archive filter
    # --------------------------------------------------------

    statement = select(Event).where(
        Event.is_archived.is_(archived)
    )

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    if search:
        search_pattern = f"%{search.strip()}%"

        statement = statement.where(
            or_(
                Event.title.ilike(search_pattern),
                Event.description.ilike(search_pattern),
            )
        )

    # --------------------------------------------------------
    # Venue filter
    # --------------------------------------------------------

    if venue:
        statement = statement.where(
            Event.venue.ilike(
                f"%{venue.strip()}%"
            )
        )

    # --------------------------------------------------------
    # Event date filter
    # --------------------------------------------------------

    if event_date:

        start_of_day = datetime.combine(
            event_date,
            time.min,
        )

        start_of_next_day = (
            start_of_day + timedelta(days=1)
        )

        statement = statement.where(
            Event.start_date >= start_of_day,
            Event.start_date < start_of_next_day,
        )

    # --------------------------------------------------------
    # Sorting
    # --------------------------------------------------------

    if sort_by == "title":
        sort_column = Event.title

    elif sort_by == "venue":
        sort_column = Event.venue

    else:
        sort_column = Event.start_date

    if sort_order.lower() == "desc":

        statement = statement.order_by(
            sort_column.desc()
        )

    else:

        statement = statement.order_by(
            sort_column.asc()
        )

    # --------------------------------------------------------
    # Pagination
    # --------------------------------------------------------

    offset = (page - 1) * page_size

    statement = (
        statement
        .offset(offset)
        .limit(page_size)
    )

    return list(
        db.scalars(statement).all()
    )


# ============================================================
# GET EVENT DETAILS
# ============================================================

def get_event_detail(
    db: Session,
    event_id: int,
    user_id: int,
) -> dict | None:

    event = get_event(
        db=db,
        event_id=event_id,
    )

    if event is None:
        return None

    # --------------------------------------------------------
    # Archived events are hidden from normal detail view
    # --------------------------------------------------------

    if event.is_archived:
        return None

    # --------------------------------------------------------
    # Count active registrations
    # --------------------------------------------------------

    active_registrations = (
        db.query(func.count(Registration.id))
        .join(
            EventSession,
            Registration.session_id == EventSession.id,
        )
        .filter(
            EventSession.event_id == event_id,
            Registration.status.in_(
                ACTIVE_STATUSES
            ),
        )
        .scalar()
        or 0
    )

    # --------------------------------------------------------
    # Calculate available seats
    # --------------------------------------------------------

    available_seats = max(
        event.capacity - active_registrations,
        0,
    )

    # --------------------------------------------------------
    # Check user's active registration
    # --------------------------------------------------------

    user_registration = (
        db.query(Registration.id)
        .join(
            EventSession,
            Registration.session_id == EventSession.id,
        )
        .filter(
            EventSession.event_id == event_id,
            Registration.user_id == user_id,
            Registration.status.in_(
                ACTIVE_STATUSES
            ),
        )
        .first()
    )

    if user_registration is None:
        registration_status = "not_registered"
    else:
        registration_status = "registered"

    # --------------------------------------------------------
    # Return event details
    # --------------------------------------------------------

    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "venue": event.venue,
        "start_date": event.start_date,
        "end_date": event.end_date,
        "capacity": event.capacity,
        "available_seats": available_seats,
        "is_archived": event.is_archived,
        "organizer_id": event.organizer_id,
        "registration_status": registration_status,
    }


# ============================================================
# GET EVENT STATISTICS
# ============================================================

def get_event_stats(
    db: Session,
    event_id: int,
    organizer_id: int,
) -> dict:

    event = get_event(
        db=db,
        event_id=event_id,
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
                "for your own events"
            ),
        )

    total_registrations = (
        db.query(func.count(Registration.id))
        .join(
            EventSession,
            Registration.session_id == EventSession.id,
        )
        .filter(
            EventSession.event_id == event_id,
        )
        .scalar()
        or 0
    )

    active_registrations = (
        db.query(func.count(Registration.id))
        .join(
            EventSession,
            Registration.session_id == EventSession.id,
        )
        .filter(
            EventSession.event_id == event_id,
            Registration.status.in_(
                ACTIVE_STATUSES
            ),
        )
        .scalar()
        or 0
    )

    cancelled_registrations = (
        db.query(func.count(Registration.id))
        .join(
            EventSession,
            Registration.session_id == EventSession.id,
        )
        .filter(
            EventSession.event_id == event_id,
            Registration.status == "cancelled",
        )
        .scalar()
        or 0
    )

    available_seats = max(
        event.capacity - active_registrations,
        0,
    )

    return {
        "event_id": event.id,
        "capacity": event.capacity,
        "total_registrations": total_registrations,
        "active_registrations": active_registrations,
        "cancelled_registrations": cancelled_registrations,
        "available_seats": available_seats,
    }


# ============================================================
# UPDATE EVENT
# ============================================================

def update_event(
    db: Session,
    event: Event,
    event_data: EventUpdate,
) -> Event:

    update_data = event_data.model_dump(
        exclude_unset=True
    )

    new_start_date = update_data.get(
        "start_date",
        event.start_date,
    )

    new_end_date = update_data.get(
        "end_date",
        event.end_date,
    )

    if new_end_date <= new_start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_date must be after start_date",
        )

    if "capacity" in update_data:

        new_capacity = update_data["capacity"]

        active_registrations = (
            db.query(func.count(Registration.id))
            .join(
                EventSession,
                Registration.session_id
                == EventSession.id,
            )
            .filter(
                EventSession.event_id == event.id,
                Registration.status.in_(
                    ACTIVE_STATUSES
                ),
            )
            .scalar()
            or 0
        )

        if new_capacity < active_registrations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Capacity cannot be less than "
                    "the number of active registrations "
                    f"({active_registrations})"
                ),
            )

    if "title" in update_data:
        update_data["title"] = (
            update_data["title"].strip()
        )

    if "venue" in update_data:
        update_data["venue"] = (
            update_data["venue"].strip()
        )

    for field, value in update_data.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)

    return event


# ============================================================
# ARCHIVE EVENT
# ============================================================

def archive_event(
    db: Session,
    event: Event,
) -> Event:

    if event.is_archived:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is already archived",
        )

    event.is_archived = True

    db.commit()
    db.refresh(event)

    return event


# ============================================================
# RESTORE EVENT
# ============================================================

def restore_event(
    db: Session,
    event: Event,
) -> Event:

    if not event.is_archived:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is already active",
        )

    event.is_archived = False

    db.commit()
    db.refresh(event)

    return event


# ============================================================
# DELETE EVENT
# ============================================================

def delete_event(
    db: Session,
    event: Event,
) -> None:

    db.delete(event)
    db.commit()