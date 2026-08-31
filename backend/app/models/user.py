from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.session_staff import SessionStaff

class User(Base):
    __tablename__ = "users"

    # ============================================================
    # PRIMARY KEY
    # ============================================================

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    # ============================================================
    # USER DETAILS
    # ============================================================

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # ============================================================
    # ROLE
    # organizer / checkin_staff / attendee
    # ============================================================

    role: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="attendee",
        index=True,
    )

    # ============================================================
    # ACCOUNT STATUS
    # ============================================================

    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    # ============================================================
    # EVENTS CREATED BY THIS USER
    # ============================================================

    events: Mapped[list["Event"]] = relationship(
        back_populates="organizer",
    )

    # ============================================================
    # REGISTRATIONS CREATED BY THIS USER
    # ============================================================

    registrations: Mapped[list["Registration"]] = relationship(
        back_populates="user",
    )

    # ============================================================
    # SESSIONS ASSIGNED TO THIS STAFF MEMBER
    # ============================================================

    assigned_sessions: Mapped[list["Session"]] = relationship(
        "Session",
        secondary=SessionStaff.__table__,
        back_populates="assigned_staff",
    )