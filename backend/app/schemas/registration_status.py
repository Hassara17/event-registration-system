from pydantic import BaseModel


class RegistrationStatusResponse(BaseModel):
    session_id: int
    capacity: int
    available_seats: int
    registration_status: str