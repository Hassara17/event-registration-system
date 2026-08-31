from pydantic import BaseModel, Field,EmailStr
from typing import Literal

class UserUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )


class UserCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=72,
    )

    role: Literal[
        "organizer",
        "checkin_staff",
        "attendee",
    ]