from datetime import date, datetime, time, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.registration import Registration
from app.schemas.event import EventCreate, EventUpdate


def create_event(
    db: Session,
    event_data: EventCreate,
    organizer_id: int,
) -> Event:
    event = Event(
        title=event_data.title,
        description=event_data.description,
        venue=event_data.venue,
        start_date=event_data.start_date,
        end_date=event_data.end_date,
        capacity=event_data.capacity,
        is_published=event_data.is_published,
        organizer_id=organizer_id,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


def get_event(
    db: Session,
    event_id: int,
) -> Event | None:
    statement = select(Event).where(
        Event.id == event_id
    )

    return db.scalar(statement)


def get_events(
    db: Session,
    search: str | None = None,
    venue: str | None = None,
    event_date: date | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "start_date",
    sort_order: str = "asc",
) -> list[Event]:
    """
    Return published events with filtering,
    pagination, and sorting.

    Filters:
    - search: searches title and description
    - venue: searches venue
    - event_date: matches events starting on that date

    Pagination:
    - page: page number starting from 1
    - page_size: number of events per page

    Sorting:
    - sort_by: start_date, title, or venue
    - sort_order: asc or desc
    """

    # Only published events are visible to users
    statement = select(Event).where(
        Event.is_published.is_(True)
    )

    # --------------------------------------------------
    # Search by title OR description
    # --------------------------------------------------

    if search:
        search_pattern = f"%{search}%"

        statement = statement.where(
            or_(
                Event.title.ilike(search_pattern),
                Event.description.ilike(search_pattern),
            )
        )

    # --------------------------------------------------
    # Filter by venue
    # --------------------------------------------------

    if venue:
        statement = statement.where(
            Event.venue.ilike(f"%{venue}%")
        )

    # --------------------------------------------------
    # Filter by event date
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Sorting
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Pagination
    # --------------------------------------------------

    offset = (page - 1) * page_size

    statement = statement.offset(
        offset
    ).limit(
        page_size
    )

    return list(
        db.scalars(statement).all()
    )


def get_event_detail(
    db: Session,
    event_id: int,
    user_id: int,
) -> dict | None:
    """
    Return detailed event information for a user,
    including available seats and the user's
    registration status.
    """

    # 1. Get the event
    event = get_event(
        db=db,
        event_id=event_id,
    )

    if event is None:
        return None

    # 2. Count active registrations
    active_registrations = (
        db.query(func.count(Registration.id))
        .filter(
            Registration.event_id == event_id,
            Registration.status == "registered",
        )
        .scalar()
    )

    # 3. Calculate available seats
    available_seats = (
        event.capacity - active_registrations
    )

    # Prevent negative available seats
    if available_seats < 0:
        available_seats = 0

    # 4. Get the user's latest registration
    registration = (
        db.query(Registration)
        .filter(
            Registration.event_id == event_id,
            Registration.user_id == user_id,
        )
        .order_by(
            Registration.id.desc()
        )
        .first()
    )

    # 5. Determine registration status
    if registration is None:
        registration_status = "not_registered"

    elif registration.status == "registered":
        registration_status = "registered"

    elif registration.status == "cancelled":
        registration_status = "cancelled"

    else:
        registration_status = registration.status

    # 6. Return combined event details
    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "venue": event.venue,
        "start_date": event.start_date,
        "end_date": event.end_date,
        "capacity": event.capacity,
        "available_seats": available_seats,
        "is_published": event.is_published,
        "organizer_id": event.organizer_id,
        "registration_status": registration_status,
    }


def update_event(
    db: Session,
    event: Event,
    event_data: EventUpdate,
) -> Event:
    update_data = event_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            event,
            field,
            value,
        )

    db.commit()
    db.refresh(event)

    return event


def delete_event(
    db: Session,
    event: Event,
) -> None:
    db.delete(event)
    db.commit()

