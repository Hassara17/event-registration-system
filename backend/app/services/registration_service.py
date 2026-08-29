from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.registration import Registration


def create_registration(
    db: Session,
    event_id: int,
    user_id: int,
) -> Registration:
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

    # 2. Check that the event is published
    if not event.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is not published",
        )

    # 3. Check if the user has already registered
    existing_registration = (
        db.query(Registration)
        .filter(
            Registration.user_id == user_id,
            Registration.event_id == event_id,
            Registration.status == "registered",
        )
        .first()
    )

    if existing_registration is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are already registered for this event",
        )

    # 4. Count current active registrations
    registration_count = (
        db.query(func.count(Registration.id))
        .filter(
            Registration.event_id == event_id,
            Registration.status == "registered",
        )
        .scalar()
    )

    # 5. Check event capacity
    if registration_count >= event.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event capacity is full",
        )

    # 6. Create registration
    registration = Registration(
        user_id=user_id,
        event_id=event_id,
        status="registered",
    )

    db.add(registration)
    db.commit()
    db.refresh(registration)

    return registration


def get_user_registrations(
    db: Session,
    user_id: int,
) -> list[Registration]:
    return (
        db.query(Registration)
        .filter(
            Registration.user_id == user_id,
            Registration.status == "registered",
        )
        .all()
    )


def cancel_registration(
    db: Session,
    event_id: int,
    user_id: int,
) -> Registration:
    # 1. Find the user's active registration
    registration = (
        db.query(Registration)
        .filter(
            Registration.event_id == event_id,
            Registration.user_id == user_id,
            Registration.status == "registered",
        )
        .first()
    )

    # 2. Registration doesn't exist
    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )

    # 3. Cancel instead of deleting the record
    registration.status = "cancelled"

    db.commit()
    db.refresh(registration)

    return registration


def get_event_registrations(
    db: Session,
    event_id: int,
    organizer_id: int,
) -> list[Registration]:
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

    # 2. Check that the current user owns the event
    if event.organizer_id != organizer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view registrations for your own events",
        )

    # 3. Return active registrations
    return (
        db.query(Registration)
        .filter(
            Registration.event_id == event_id,
            Registration.status == "registered",
        )
        .all()
    )