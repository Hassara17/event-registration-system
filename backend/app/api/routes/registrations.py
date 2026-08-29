from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.registration import (
    RegistrationCreate,
    RegistrationResponse,
)
from app.services.registration_service import (
    cancel_registration,
    create_registration,
    get_user_registrations,
)


router = APIRouter(
    prefix="/registrations",
    tags=["Registrations"],
)


@router.post(
    "",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_for_event(
    registration_data: RegistrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_registration(
        db=db,
        event_id=registration_data.event_id,
        user_id=current_user.id,
    )


@router.get(
    "/me",
    response_model=list[RegistrationResponse],
)
def get_my_registrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_registrations(
        db=db,
        user_id=current_user.id,
    )


@router.delete(
    "/{event_id}",
    response_model=RegistrationResponse,
)
def cancel_event_registration(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return cancel_registration(
        db=db,
        event_id=event_id,
        user_id=current_user.id,
    )