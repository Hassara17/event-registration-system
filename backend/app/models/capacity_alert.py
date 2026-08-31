from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
)

from sqlalchemy.orm import Mapped, mapped_column,relationship

from app.core.database import Base


class CapacityAlert(Base):
    __tablename__ = "capacity_alerts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    session_id: Mapped[int] = mapped_column(
        ForeignKey(
            "sessions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    dismissed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    dismissed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    last_filled_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    session: Mapped["Session"] = relationship(
        "Session",
        back_populates="capacity_alert",
    )