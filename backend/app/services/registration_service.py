from datetime import datetime

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

    # 3. Check that the event has not started
    if event.start_date <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Registration is closed because the event "
                "has already started or passed"
            ),
        )

    # 4. Check if the user has already registered
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

    # 5. Count current active registrations
    registration_count = (
        db.query(func.count(Registration.id))
        .filter(
            Registration.event_id == event_id,
            Registration.status == "registered",
        )
        .scalar()
    )

    # 6. Check event capacity
    if registration_count >= event.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event capacity is full",
        )

    # 7. Create registration
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

    # 2. Check that the event has not started
    if event.start_date <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Registration cannot be cancelled because "
                "the event has already started or passed"
            ),
        )

    # 3. Find the user's active registration
    registration = (
        db.query(Registration)
        .filter(
            Registration.event_id == event_id,
            Registration.user_id == user_id,
            Registration.status == "registered",
        )
        .first()
    )

    # 4. Registration doesn't exist
    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )

    # 5. Cancel instead of deleting the record
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
            detail=(
                "You can only view registrations "
                "for your own events"
            ),
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


def get_event_stats(
    db: Session,
    event_id: int,
    organizer_id: int,
) -> dict:
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

    # 2. Check that the organizer owns the event
    if event.organizer_id != organizer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only view statistics "
                "for your own events"
            ),
        )

    # 3. Count active registrations
    active_registrations = (
        db.query(func.count(Registration.id))
        .filter(
            Registration.event_id == event_id,
            Registration.status == "registered",
        )
        .scalar()
    )

    # 4. Count cancelled registrations
    cancelled_registrations = (
        db.query(func.count(Registration.id))
        .filter(
            Registration.event_id == event_id,
            Registration.status == "cancelled",
        )
        .scalar()
    )

    # 5. Calculate total registrations
    total_registrations = (
        active_registrations
        + cancelled_registrations
    )

    # 6. Calculate available seats
    available_seats = (
        event.capacity
        - active_registrations
    )

    return {
        "event_id": event.id,
        "capacity": event.capacity,
        "total_registrations": total_registrations,
        "active_registrations": active_registrations,
        "cancelled_registrations": cancelled_registrations,
        "available_seats": available_seats,
    }


def get_registration_status(
    db: Session,
    event_id: int,
    user_id: int,
) -> dict:
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
        event.capacity
        - active_registrations
    )

    # 4. Get the user's latest registration
    registration = (
        db.query(Registration)
        .filter(
            Registration.event_id == event_id,
            Registration.user_id == user_id,
        )
        .order_by(Registration.id.desc())
        .first()
    )

    # 5. Determine the user's registration status
    if registration is None:
        registration_status = "not_registered"

    elif registration.status == "registered":
        registration_status = "registered"

    elif registration.status == "cancelled":
        registration_status = "cancelled"

    else:
        registration_status = registration.status

    return {
        "event_id": event.id,
        "capacity": event.capacity,
        "available_seats": available_seats,
        "registration_status": registration_status,
    }