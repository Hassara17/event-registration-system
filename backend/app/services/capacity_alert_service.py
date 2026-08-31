from datetime import datetime

from fastapi import HTTPException, status

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.capacity_alert import CapacityAlert
from app.models.registration import Registration
from app.models.session import Session as EventSession
from app.models.event import Event


ACTIVE_STATUSES = (
    "reserved",
    "confirmed",
    "checked_in",
)


def get_active_registration_count(
    db: Session,
    session_id: int,
) -> int:

    return (
        db.query(func.count(Registration.id))
        .filter(
            Registration.session_id == session_id,
            Registration.status.in_(ACTIVE_STATUSES),
        )
        .scalar()
        or 0
    )


def update_capacity_alert(
    db: Session,
    session_id: int,
) -> CapacityAlert | None:

    event_session = (
        db.query(EventSession)
        .filter(EventSession.id == session_id)
        .first()
    )

    if event_session is None:
        return None

    active_count = get_active_registration_count(
        db=db,
        session_id=session_id,
    )

    alert = (
        db.query(CapacityAlert)
        .filter(
            CapacityAlert.session_id == session_id
        )
        .first()
    )

    now = datetime.utcnow()

    # ========================================================
    # SESSION IS FULL
    # ========================================================

    if active_count >= event_session.capacity:

        # ----------------------------------------------------
        # First time becoming full
        # ----------------------------------------------------

        if alert is None:

            alert = CapacityAlert(
                session_id=session_id,
                is_active=True,
                dismissed=False,
                created_at=now,
                last_filled_at=now,
            )

            db.add(alert)

        # ----------------------------------------------------
        # Session became full again after previously
        # having an available seat.
        # ----------------------------------------------------

        elif not alert.is_active:

            alert.is_active = True
            alert.dismissed = False
            alert.dismissed_at = None
            alert.last_filled_at = now

    # ========================================================
    # SESSION HAS AVAILABLE SEAT
    # ========================================================

    else:

        if alert is not None:

            alert.is_active = False

    db.commit()

    if alert is not None:
        db.refresh(alert)

    return alert


def dismiss_capacity_alert(
    db: Session,
    session_id: int,
    organizer_id: int,
) -> CapacityAlert:

    alert = (
        db.query(CapacityAlert)
        .filter(
            CapacityAlert.session_id == session_id,
            CapacityAlert.is_active.is_(True),
        )
        .first()
    )

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active capacity alert found",
        )

    event_session = (
        db.query(EventSession)
        .filter(EventSession.id == session_id)
        .first()
    )

    if event_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    event = event_session.event

    if event is None or event.organizer_id != organizer_id:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to dismiss this alert"
            ),
        )

    alert.dismissed = True
    alert.dismissed_at = datetime.utcnow()

    db.commit()
    db.refresh(alert)

    return alert


def get_capacity_alerts(
    db: Session,
    organizer_id: int,
) -> list[CapacityAlert]:

    return (
        db.query(CapacityAlert)
        .join(
            EventSession,
            CapacityAlert.session_id == EventSession.id,
        )
        .join(
            Event,
            EventSession.event_id == Event.id,
        )
        .filter(
            Event.organizer_id == organizer_id,
            CapacityAlert.is_active.is_(True),
            CapacityAlert.dismissed.is_(False),
        )
        .order_by(
            CapacityAlert.created_at.desc()
        )
        .all()
    )