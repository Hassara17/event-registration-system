from pydantic import BaseModel


class EventStatsResponse(BaseModel):
    event_id: int
    capacity: int
    total_registrations: int
    active_registrations: int
    cancelled_registrations: int
    available_seats: int