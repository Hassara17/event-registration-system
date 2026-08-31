from datetime import datetime
from sqlalchemy.orm import relationship

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

from app.core.database import Base


class RegistrationHistory(Base):
    __tablename__ = "registration_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    registration_id = Column(
        Integer,
        ForeignKey(
            "registrations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    action = Column(
        String(50),
        nullable=False,
    )

    old_status = Column(
        String(30),
        nullable=True,
    )

    new_status = Column(
        String(30),
        nullable=True,
    )

    note = Column(
        Text,
        nullable=True,
    )

    actor_user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    registration = relationship(
        "Registration",
        back_populates="history",
    )