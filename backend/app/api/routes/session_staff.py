from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.api.deps import (
    get_db,
    require_role,
)

from app.models.event import Event
from app.models.session import Session as EventSession
from app.models.session_staff import SessionStaff
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
# GET STAFF ASSIGNED TO A SESSION
# Organizer only
# ============================================================

@router.get("/{session_id}/staff")
def get_session_staff_endpoint(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):
    # --------------------------------------------------------
    # Find session
    # --------------------------------------------------------

    event_session = (
        db.query(EventSession)
        .filter(
            EventSession.id == session_id,
        )
        .first()
    )

    if event_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # --------------------------------------------------------
    # Find parent event
    # --------------------------------------------------------

    event = (
        db.query(Event)
        .filter(
            Event.id == event_session.event_id,
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    # --------------------------------------------------------
    # Verify organizer owns the event
    # --------------------------------------------------------

    if event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view staff for your own events",
        )

    # --------------------------------------------------------
    # Get assigned staff
    # --------------------------------------------------------

    staff_users = (
        db.query(User)
        .join(
            SessionStaff,
            SessionStaff.staff_id == User.id,
        )
        .filter(
            SessionStaff.session_id == session_id,
            User.role == "checkin_staff",
            User.is_active == True,
        )
        .order_by(
            User.name.asc()
        )
        .all()
    )

    # --------------------------------------------------------
    # Return clean response
    # --------------------------------------------------------

    return [
        {
            "id": staff.id,
            "name": staff.name,
            "email": staff.email,
            "role": staff.role,
            "is_active": staff.is_active,
        }
        for staff in staff_users
    ]


# ============================================================
# GET CURRENT STAFF MEMBER'S ASSIGNED SESSIONS
# Check-in staff only
# ============================================================

@router.get("/my/assigned")
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