from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import User
from app.schemas.registration import RegistrationResponse
from app.services.registration_service import (
    get_session_registrations,
    get_session_stats,
)


router = APIRouter(
    prefix="/organizer",
    tags=["Organizer"],
)


# ============================================================
# GET SESSION REGISTRATIONS
# ============================================================

@router.get(
    "/sessions/{session_id}/registrations",
    response_model=list[RegistrationResponse],
)
def get_session_registrations_endpoint(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):
    return get_session_registrations(
        db=db,
        session_id=session_id,
        organizer_id=current_user.id,
    )


# ============================================================
# GET SESSION REGISTRATION STATS
# ============================================================

@router.get(
    "/sessions/{session_id}/stats",
)
def get_session_stats_endpoint(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):
    return get_session_stats(
        db=db,
        session_id=session_id,
        organizer_id=current_user.id,
    )