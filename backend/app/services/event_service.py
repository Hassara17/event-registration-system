from sqlalchemy import select
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
    statement = select(Event).where(Event.id == event_id)

    return db.scalar(statement)


def get_events(
    db: Session,
) -> list[Event]:
    statement = select(Event).order_by(Event.id.desc())

    return list(db.scalars(statement).all())


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