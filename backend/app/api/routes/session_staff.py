from fastapi import (
    APIRouter,
    Depends,
    status,
)

from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_user,
    get_db,
    require_role,
)

from app.models.user import User

from app.services.session_staff_service import (
    assign_staff_to_session,
    get_staff_assigned_sessions,
    remove_staff_from_session,
)


router = APIRouter(
    prefix="/sessions",
    tags=["Session Staff"],
)


# ============================================================
# ASSIGN CHECK-IN STAFF TO SESSION
# ============================================================

@router.post(
    "/{session_id}/staff/{staff_id}",
    status_code=status.HTTP_201_CREATED,
)
def assign_staff_endpoint(
    session_id: int,
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):
    return assign_staff_to_session(
        db=db,
        session_id=session_id,
        staff_id=staff_id,
        organizer_id=current_user.id,
    )


# ============================================================
# REMOVE CHECK-IN STAFF FROM SESSION
# ============================================================

@router.delete(
    "/{session_id}/staff/{staff_id}",
)
def remove_staff_endpoint(
    session_id: int,
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):
    return remove_staff_from_session(
        db=db,
        session_id=session_id,
        staff_id=staff_id,
        organizer_id=current_user.id,
    )


# ============================================================
# GET MY ASSIGNED SESSIONS
# ============================================================

@router.get(
    "/my/assigned",
)
def get_my_assigned_sessions_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("checkin_staff")
    ),
):
    return get_staff_assigned_sessions(
        db=db,
        staff_id=current_user.id,
    )