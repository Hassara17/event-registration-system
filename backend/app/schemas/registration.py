from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


# ============================================================
# CREATE REGISTRATION
# ============================================================

class RegistrationCreate(BaseModel):

    session_id: int

    attendee_name: str = Field(
        min_length=1,
        max_length=100,
    )

    attendee_email: EmailStr


# ============================================================
# REGISTRATION RESPONSE
# ============================================================

class RegistrationResponse(BaseModel):

    id: int

    user_id: int | None

    session_id: int

    attendee_name: str

    attendee_email: EmailStr

    status: str

    reserved_at: datetime

    confirmed_at: datetime | None

    checked_in_at: datetime | None

    cancelled_at: datetime | None

    expired_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True,
    )


# ============================================================
# REGISTRATION HISTORY
# ============================================================

class RegistrationHistoryResponse(BaseModel):

    id: int

    session_id: int
    session_title: str

    event_id: int
    event_title: str

    venue: str

    attendee_name: str
    attendee_email: EmailStr

    start_time: datetime

    status: str

    reserved_at: datetime

    confirmed_at: datetime | None

    checked_in_at: datetime | None

    cancelled_at: datetime | None

    expired_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True,
    )


# ============================================================
# SESSION REGISTRATION STATISTICS
# ============================================================

class SessionStatsResponse(BaseModel):

    session_id: int

    session_title: str

    capacity: int

    reserved: int

    confirmed: int

    checked_in: int

    cancelled: int

    expired: int

    active_registrations: int

    available_seats: int


# ============================================================
# REGISTRATION STATUS
# ============================================================

class RegistrationStatusResponse(BaseModel):

    session_id: int

    capacity: int

    available_seats: int

    registration_status: str


# ============================================================
# REGISTRATION SEARCH ITEM
# ============================================================

class RegistrationSearchItem(BaseModel):

    id: int

    user_id: int | None

    session_id: int

    attendee_name: str

    attendee_email: EmailStr

    status: str

    reserved_at: datetime

    confirmed_at: datetime | None

    checked_in_at: datetime | None

    cancelled_at: datetime | None

    expired_at: datetime | None

    session_title: str

    event_id: int

    event_title: str

    model_config = ConfigDict(
        from_attributes=True,
    )


# ============================================================
# REGISTRATION SEARCH RESPONSE
# ============================================================

class RegistrationSearchResponse(BaseModel):

    items: list[RegistrationSearchItem]

    total: int

    page: int

    page_size: int

    total_pages: int


# ============================================================
# REGISTRATION SEARCH QUERY
# ============================================================

class RegistrationSearchQuery(BaseModel):

    search: str | None = Field(
        default=None,
        max_length=255,
    )

    event_id: int | None = None

    session_id: int | None = None

    registration_status: str | None = None

    sort_by: str = Field(
        default="reserved_at",
    )

    sort_order: str = Field(
        default="desc",
    )

    page: int = Field(
        default=1,
        ge=1,
    )

    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
    )

# ============================================================
# BULK IMPORT RESULT
# ============================================================

class BulkImportRowResult(BaseModel):
    row_number: int
    attendee_name: str | None = None
    attendee_email: str | None = None
    result: str
    reason: str | None = None
    registration_id: int | None = None


class BulkImportResponse(BaseModel):
    session_id: int
    total_rows: int
    created: int
    duplicates: int
    rejected: int
    rows: list[BulkImportRowResult]

# ============================================================
# REGISTRATION HISTORY TIMELINE
# ============================================================

class RegistrationHistoryItem(BaseModel):

    id: int

    registration_id: int

    action: str

    old_status: str | None

    new_status: str | None

    note: str | None

    actor_user_id: int | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class RegistrationHistoryListResponse(BaseModel):

    registration_id: int

    items: list[RegistrationHistoryItem]


# ============================================================
# REGISTRATION NOTE
# ============================================================

class RegistrationNoteCreate(BaseModel):

    note: str = Field(
        min_length=1,
        max_length=2000,
    )



# ============================================================
# REGISTRATION HISTORY TIMELINE
# ============================================================

class RegistrationHistoryItemResponse(BaseModel):
    id: int
    registration_id: int
    action: str
    old_status: str | None
    new_status: str | None
    note: str | None
    actor_user_id: int | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )