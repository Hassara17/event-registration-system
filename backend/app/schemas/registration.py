from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RegistrationCreate(BaseModel):
    event_id: int


class RegistrationResponse(BaseModel):
    id: int
    user_id: int
    event_id: int
    registered_at: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)