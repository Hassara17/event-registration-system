from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.core.database import Base
from app.models.session_staff import SessionStaff
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Session(Base):
    __tablename__ = "sessions"

    # ========================================================
    # PRIMARY KEY
    # ========================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ========================================================
    # EVENT
    # ========================================================

    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id"),
        nullable=False,
        index=True,
    )

    # ========================================================
    # SESSION DETAILS
    # ========================================================

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    location: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # ========================================================
    # CONSTRAINTS
    # ========================================================

    __table_args__ = (
        CheckConstraint(
            "duration > 0",
            name="check_session_duration_positive",
        ),
        CheckConstraint(
            "capacity > 0",
            name="check_session_capacity_positive",
        ),
    )

    # ========================================================
    # RELATIONSHIP WITH EVENT
    # ========================================================

    event: Mapped["Event"] = relationship(
        "Event",
        back_populates="sessions",
    )

    # ========================================================
    # RELATIONSHIP WITH REGISTRATIONS
    # ========================================================

    registrations: Mapped[list["Registration"]] = relationship(
        "Registration",
        back_populates="session",
        cascade="all, delete-orphan",
    )

    # ========================================================
    # RELATIONSHIP WITH CHECK-IN STAFF
    # ========================================================

    assigned_staff: Mapped[list["User"]] = relationship(
        "User",
        secondary=SessionStaff.__table__,
        back_populates="assigned_sessions",
    )
    event: Mapped["Event"] = relationship(
        "Event",
        back_populates="sessions",
    )

    registrations: Mapped[list["Registration"]] = relationship(
        "Registration",
        back_populates="session",
    )

    assigned_staff: Mapped[list["User"]] = relationship(
        "User",
        secondary=SessionStaff.__table__,
        back_populates="assigned_sessions",
    )

    capacity_alert: Mapped["CapacityAlert | None"] = relationship(
        "CapacityAlert",
        back_populates="session",
        uselist=False,
    )