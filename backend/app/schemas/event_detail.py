from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EventDetailResponse(BaseModel):
    id: int
    title: str
    description: str | None
    venue: str
    start_date: datetime
    end_date: datetime
    capacity: int
    available_seats: int
    is_archived: bool
    organizer_id: int
    registration_status: str

    model_config = ConfigDict(
        from_attributes=True,
    )