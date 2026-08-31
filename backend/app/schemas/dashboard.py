from datetime import date

from pydantic import BaseModel


# ============================================================
# REGISTRATION STATUS BREAKDOWN
# ============================================================

class RegistrationStatusBreakdown(BaseModel):
    reserved: int
    confirmed: int
    checked_in: int
    cancelled: int
    expired: int


# ============================================================
# REGISTRATION BY SESSION
# ============================================================

class SessionRegistrationBreakdown(BaseModel):
    session_id: int
    session_title: str
    capacity: int
    registrations: int


# ============================================================
# DAILY CHECK-IN
# ============================================================

class DailyCheckin(BaseModel):
    date: date
    checked_in: int


# ============================================================
# DASHBOARD RESPONSE
# ============================================================

class DashboardResponse(BaseModel):

    # --------------------------------------------------------
    # Headline metrics
    # --------------------------------------------------------

    sessions_today: int

    checked_in_today: int

    expired_this_week: int

    sessions_at_capacity: int

    # --------------------------------------------------------
    # Registration breakdown
    # --------------------------------------------------------

    registrations_by_status: RegistrationStatusBreakdown

    # --------------------------------------------------------
    # Session breakdown
    # --------------------------------------------------------

    registrations_by_session: list[
        SessionRegistrationBreakdown
    ]

    # --------------------------------------------------------
    # 14-day check-in chart
    # --------------------------------------------------------

    checkins_last_14_days: list[DailyCheckin]