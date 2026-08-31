from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.session import Session as EventSession
from app.models.session_staff import SessionStaff
from app.models.user import User


# ============================================================
# ASSIGN CHECK-IN STAFF TO SESSION
# ============================================================

def assign_staff_to_session(
    db: Session,
    session_id: int,
    staff_id: int,
    organizer_id: int,
) -> dict:

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

    if event.organizer_id != organizer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only assign staff "
                "to your own events"
            ),
        )

    # --------------------------------------------------------
    # Find staff user
    # --------------------------------------------------------

    staff = (
        db.query(User)
        .filter(
            User.id == staff_id,
        )
        .first()
    )

    if staff is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff user not found",
        )

    # --------------------------------------------------------
    # Verify check-in staff role
    # --------------------------------------------------------

    if staff.role != "checkin_staff":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected user is not check-in staff",
        )

    # --------------------------------------------------------
    # Verify account is active
    # --------------------------------------------------------

    if not staff.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Staff account is inactive",
        )

    # --------------------------------------------------------
    # Prevent duplicate assignment
    # --------------------------------------------------------

    existing_assignment = (
        db.query(SessionStaff)
        .filter(
            SessionStaff.session_id == session_id,
            SessionStaff.staff_id == staff_id,
        )
        .first()
    )

    if existing_assignment is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Staff member is already assigned to this session",
        )

    # --------------------------------------------------------
    # Create assignment
    # --------------------------------------------------------

    assignment = SessionStaff(
        session_id=session_id,
        staff_id=staff_id,
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return {
        "message": "Staff assigned successfully",
        "session_id": session_id,
        "staff_id": staff_id,
    }


# ============================================================
# REMOVE CHECK-IN STAFF FROM SESSION
# ============================================================

def remove_staff_from_session(
    db: Session,
    session_id: int,
    staff_id: int,
    organizer_id: int,
) -> dict:

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

    if event.organizer_id != organizer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only remove staff "
                "from your own events"
            ),
        )

    # --------------------------------------------------------
    # Find assignment
    # --------------------------------------------------------

    assignment = (
        db.query(SessionStaff)
        .filter(
            SessionStaff.session_id == session_id,
            SessionStaff.staff_id == staff_id,
        )
        .first()
    )

    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member is not assigned to this session",
        )

    # --------------------------------------------------------
    # Remove assignment
    # --------------------------------------------------------

    db.delete(assignment)
    db.commit()

    return {
        "message": "Staff removed successfully",
        "session_id": session_id,
        "staff_id": staff_id,
    }


# ============================================================
# GET CHECK-IN STAFF'S ASSIGNED SESSIONS
# ============================================================

def get_staff_assigned_sessions(
    db: Session,
    staff_id: int,
) -> list[EventSession]:

    # --------------------------------------------------------
    # Verify staff exists
    # --------------------------------------------------------

    staff = (
        db.query(User)
        .filter(
            User.id == staff_id,
        )
        .first()
    )

    if staff is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # --------------------------------------------------------
    # Verify check-in staff role
    # --------------------------------------------------------

    if staff.role != "checkin_staff":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only check-in staff can view assigned sessions",
        )

    # --------------------------------------------------------
    # Verify account is active
    # --------------------------------------------------------

    if not staff.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff account is inactive",
        )

    # --------------------------------------------------------
    # Get assigned sessions
    # --------------------------------------------------------

    return (
        db.query(EventSession)
        .join(
            SessionStaff,
            SessionStaff.session_id == EventSession.id,
        )
        .filter(
            SessionStaff.staff_id == staff_id,
        )
        .order_by(
            EventSession.start_time.asc(),
        )
        .all()
    )