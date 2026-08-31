from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CapacityAlertResponse(BaseModel):
    id: int
    session_id: int
    is_active: bool
    dismissed: bool
    created_at: datetime
    dismissed_at: datetime | None = None
    last_filled_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )