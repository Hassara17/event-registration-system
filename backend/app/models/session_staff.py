from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SessionStaff(Base):
    __tablename__ = "session_staff"

    session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sessions.id", ondelete="CASCADE"),
        primary_key=True,
    )

    staff_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )