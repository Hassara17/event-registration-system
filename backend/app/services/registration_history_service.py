from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.registration import Registration
from app.models.registration_history import RegistrationHistory


# ============================================================
# CREATE HISTORY ENTRY
# ============================================================

def create_history_entry(
    db: Session,
    registration_id: int,
    action: str,
    actor_user_id: int | None = None,
    old_status: str | None = None,
    new_status: str | None = None,
    note: str | None = None,
) -> RegistrationHistory:
    """
    Create an immutable registration history entry.

    This function only adds the history record to the current
    database transaction. The caller is responsible for commit.

    Typical actions:
        created
        confirmed
        checked_in
        cancelled
        expired
        note
    """

    history = RegistrationHistory(
        registration_id=registration_id,
        action=action,
        old_status=old_status,
        new_status=new_status,
        actor_user_id=actor_user_id,
        note=note,
        created_at=datetime.utcnow(),
    )

    db.add(history)

    return history


# ============================================================
# GET REGISTRATION HISTORY
# ============================================================

def get_registration_history(
    db: Session,
    registration_id: int,
) -> list[RegistrationHistory]:
    """
    Return the complete immutable history timeline
    for a registration.

    History is returned oldest first so the complete
    registration lifecycle can be followed chronologically.
    """

    # --------------------------------------------------------
    # Verify registration exists
    # --------------------------------------------------------

    registration = (
        db.query(Registration)
        .filter(
            Registration.id == registration_id,
        )
        .first()
    )

    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )

    # --------------------------------------------------------
    # Return history
    # --------------------------------------------------------

    return (
        db.query(RegistrationHistory)
        .filter(
            RegistrationHistory.registration_id
            == registration_id
        )
        .order_by(
            RegistrationHistory.created_at.asc(),
            RegistrationHistory.id.asc(),
        )
        .all()
    )


# ============================================================
# ADD REGISTRATION NOTE
# ============================================================

def add_registration_note(
    db: Session,
    registration_id: int,
    actor_user_id: int,
    note: str,
) -> RegistrationHistory:
    """
    Add a note to a registration's history.

    Notes do not change the registration status.
    """

    # --------------------------------------------------------
    # Verify registration exists
    # --------------------------------------------------------

    registration = (
        db.query(Registration)
        .filter(
            Registration.id == registration_id,
        )
        .first()
    )

    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )

    # --------------------------------------------------------
    # Validate note
    # --------------------------------------------------------

    note = note.strip()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Note cannot be empty",
        )

    if len(note) > 2000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Note cannot exceed 2000 characters",
        )

    # --------------------------------------------------------
    # Create history entry
    # --------------------------------------------------------

    history = create_history_entry(
        db=db,
        registration_id=registration_id,
        action="note",
        actor_user_id=actor_user_id,
        old_status=registration.status,
        new_status=registration.status,
        note=note,
    )

    # --------------------------------------------------------
    # Commit note
    # --------------------------------------------------------

    db.commit()
    db.refresh(history)

    return history