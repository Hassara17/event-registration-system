from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Event(Base):

    __tablename__ = "events"

    # ============================================================
    # PRIMARY KEY
    # ============================================================

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ============================================================
    # EVENT DETAILS
    # ============================================================

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    venue: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    start_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    end_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    # ============================================================
    # CAPACITY
    # ============================================================

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # ============================================================
    # PUBLISH STATUS
    # ============================================================

    is_published: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    # ============================================================
    # ARCHIVE STATUS
    # ============================================================

    # False = active event
    # True  = archived event
    #
    # Archiving does NOT delete the event.
    # Sessions and registrations remain intact.

    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    # ============================================================
    # ORGANIZER
    # ============================================================

    organizer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    organizer: Mapped["User"] = relationship(
        back_populates="events",
    )

    # ============================================================
    # SESSIONS
    # ============================================================

    sessions: Mapped[list["Session"]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
    )