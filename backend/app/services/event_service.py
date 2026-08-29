from datetime import date, datetime, time, timedelta

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.event import Event
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
        # Default sorting
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


def update_event(
    db: Session,
    event: Event,
    event_data: EventUpdate,
) -> Event:
    update_data = event_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)

    return event


def delete_event(
    db: Session,
    event: Event,
) -> None:
    db.delete(event)
    db.commit()