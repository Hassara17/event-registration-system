from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SessionCreate(BaseModel):
    event_id: int

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    start_time: datetime

    duration: int = Field(
        gt=0,
        description="Session duration in minutes",
    )

    location: str = Field(
        min_length=1,
        max_length=255,
    )

    capacity: int = Field(
        gt=0,
    )


class SessionUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    start_time: datetime | None = None

    duration: int | None = Field(
        default=None,
        gt=0,
        description="Session duration in minutes",
    )

    location: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    capacity: int | None = Field(
        default=None,
        gt=0,
    )


class SessionResponse(BaseModel):
    id: int
    event_id: int
    title: str
    start_time: datetime
    duration: int
    location: str
    capacity: int

    model_config = ConfigDict(
        from_attributes=True,
    )