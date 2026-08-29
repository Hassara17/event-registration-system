from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_user,
    get_db,
    require_role,
)
from app.models.user import User
from app.schemas.event import (
    EventCreate,
    EventResponse,
    EventUpdate,
)
from app.schemas.event_stats import EventStatsResponse
from app.schemas.registration import RegistrationResponse
from app.schemas.registration_status import (
    RegistrationStatusResponse,
)
from app.services.event_service import (
    create_event,
    delete_event,
    get_event,
    get_events,
    update_event,
)
from app.services.registration_service import (
    get_event_registrations,
    get_event_stats,
    get_registration_status,
)


router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event_endpoint(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):
    return create_event(
        db=db,
        event_data=event_data,
        organizer_id=current_user.id,
    )


@router.get(
    "",
    response_model=list[EventResponse],
)
def list_events(
    search: str | None = None,
    venue: str | None = None,
    event_date: date | None = None,
    db: Session = Depends(get_db),
):
    return get_events(
        db=db,
        search=search,
        venue=venue,
        event_date=event_date,
    )


@router.get(
    "/{event_id}/registrations",
    response_model=list[RegistrationResponse],
)
def get_event_registrations_endpoint(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):
    return get_event_registrations(
        db=db,
        event_id=event_id,
        organizer_id=current_user.id,
    )


@router.get(
    "/{event_id}/stats",
    response_model=EventStatsResponse,
)
def get_event_stats_endpoint(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):
    return get_event_stats(
        db=db,
        event_id=event_id,
        organizer_id=current_user.id,
    )


@router.get(
    "/{event_id}/registration-status",
    response_model=RegistrationStatusResponse,
)
def get_registration_status_endpoint(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_registration_status(
        db=db,
        event_id=event_id,
        user_id=current_user.id,
    )


@router.get(
    "/{event_id}",
    response_model=EventResponse,
)
def get_event_endpoint(
    event_id: int,
    db: Session = Depends(get_db),
):
    event = get_event(
        db,
        event_id,
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return event


@router.patch(
    "/{event_id}",
    response_model=EventResponse,
)
def update_event_endpoint(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):
    event = get_event(
        db,
        event_id,
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    if event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own events",
        )

    return update_event(
        db=db,
        event=event,
        event_data=event_data,
    )


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_event_endpoint(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):
    event = get_event(
        db,
        event_id,
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    if event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own events",
        )

    delete_event(
        db=db,
        event=event,
    )

    return None