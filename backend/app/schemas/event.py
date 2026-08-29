from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EventCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )

    description: str | None = None

    venue: str = Field(
        min_length=1,
        max_length=255,
    )

    start_date: datetime
    end_date: datetime

    capacity: int = Field(
        gt=0,
    )

    is_published: bool = False

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError(
                "end_date must be after start_date"
            )

        return self


class EventUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    description: str | None = None

    venue: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    start_date: datetime | None = None
    end_date: datetime | None = None

    capacity: int | None = Field(
        default=None,
        gt=0,
    )

    is_published: bool | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date <= self.start_date
        ):
            raise ValueError(
                "end_date must be after start_date"
            )

        return self


class EventResponse(BaseModel):
    id: int
    title: str
    description: str | None
    venue: str
    start_date: datetime
    end_date: datetime
    capacity: int
    is_published: bool
    organizer_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )