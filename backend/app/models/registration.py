from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import (
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


class Registration(Base):
    __tablename__ = "registrations"

    # ========================================================
    # PRIMARY KEY
    # ========================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ========================================================
    # USER
    # ========================================================

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    # ========================================================
    # SESSION
    # ========================================================

    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id"),
        nullable=False,
        index=True,
    )

    # ========================================================
    # ATTENDEE INFORMATION
    # ========================================================

    attendee_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    attendee_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    # ========================================================
    # REGISTRATION STATUS
    # ========================================================

    status: Mapped[str] = mapped_column(
        String(20),
        default="reserved",
        nullable=False,
        index=True,
    )

    # ========================================================
    # TIMESTAMPS
    # ========================================================

    reserved_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    checked_in_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    expired_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    # ========================================================
    # RELATIONSHIPS
    # ========================================================

    user: Mapped["User | None"] = relationship(
        "User",
        back_populates="registrations",
    )

    session: Mapped["Session"] = relationship(
        "Session",
        back_populates="registrations",
    )

    history: Mapped[list["RegistrationHistory"]] = relationship(
        "RegistrationHistory",
        cascade="all, delete-orphan",
        back_populates="registration",
        order_by="RegistrationHistory.created_at",
    )