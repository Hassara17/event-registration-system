from pydantic import BaseModel


class RegistrationStatusResponse(BaseModel):
    event_id: int
    capacity: int
    available_seats: int
    registration_status: str