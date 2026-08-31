from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.registration import Registration
from app.models.session import Session as EventSession


# ============================================================
# DASHBOARD SERVICE
# ============================================================

def get_dashboard(
    db: Session,
    current_user,
) -> dict:
    """
    Return dashboard statistics for the current user.

    Organizer:
        Dashboard contains data from their own events.

    Check-in staff:
        Dashboard contains data from sessions assigned
        to that staff member.
    """

    # ========================================================
    # CURRENT TIME
    # ========================================================

    now = datetime.utcnow()

    today_start = datetime(
        now.year,
        now.month,
        now.day,
    )

    tomorrow_start = today_start + timedelta(days=1)

    # ========================================================
    # THIS WEEK
    # ========================================================

    # Monday of the current week
    week_start = today_start - timedelta(
        days=today_start.weekday()
    )

    # ========================================================
    # LAST 14 DAYS
    # ========================================================

    fourteen_days_start = today_start - timedelta(days=13)

    # ========================================================
    # VIEWER
    # ========================================================

    viewer_role = getattr(
        current_user,
        "role",
        None,
    )

    viewer_id = current_user.id

    # ========================================================
    # BASE SESSION QUERY
    #
    # This query determines which sessions the viewer
    # is allowed to see.
    # ========================================================

    session_query = (
        db.query(EventSession)
        .join(
            Event,
            EventSession.event_id == Event.id,
        )
    )

    # ========================================================
    # ORGANIZER VISIBILITY
    # ========================================================

    if viewer_role == "organizer":

        session_query = session_query.filter(
            Event.organizer_id == viewer_id
        )

    # ========================================================
    # CHECK-IN STAFF VISIBILITY
    # ========================================================

    elif viewer_role == "checkin_staff":

        session_query = (
            session_query
            .join(EventSession.assigned_staff)
            .filter(
                EventSession.assigned_staff.any(
                    id=viewer_id
                )
            )
        )

    # ========================================================
    # INVALID ROLE
    # ========================================================

    else:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Only organizers and check-in staff "
                "can access the dashboard"
            ),
        )

    # ========================================================
    # GET VISIBLE SESSIONS
    # ========================================================

    visible_sessions = session_query.all()

    visible_session_ids = [
        session.id
        for session in visible_sessions
    ]

    # ========================================================
    # NO VISIBLE SESSIONS
    # ========================================================

    if not visible_session_ids:

        return {
            "sessions_today": 0,

            "checked_in_today": 0,

            "expired_this_week": 0,

            "sessions_at_capacity": 0,

            "registrations_by_status": {
                "reserved": 0,
                "confirmed": 0,
                "checked_in": 0,
                "cancelled": 0,
                "expired": 0,
            },

            "registrations_by_session": [],

            "checkins_last_14_days": [
                {
                    "date": (
                        fourteen_days_start
                        + timedelta(days=i)
                    ).date(),
                    "checked_in": 0,
                }
                for i in range(14)
            ],
        }

    # ========================================================
    # 1. SESSIONS TODAY
    # ========================================================

    sessions_today = (
        session_query
        .filter(
            EventSession.start_time >= today_start,
            EventSession.start_time < tomorrow_start,
        )
        .count()
    )

    # ========================================================
    # REGISTRATION BASE QUERY
    # ========================================================

    registration_query = (
        db.query(Registration)
        .filter(
            Registration.session_id.in_(
                visible_session_ids
            )
        )
    )

    # ========================================================
    # 2. CHECKED-IN TODAY
    # ========================================================

    checked_in_today = (
        registration_query
        .filter(
            Registration.status == "checked_in",
            Registration.checked_in_at >= today_start,
            Registration.checked_in_at < tomorrow_start,
        )
        .count()
    )

    # ========================================================
    # 3. EXPIRED THIS WEEK
    # ========================================================

    expired_this_week = (
        registration_query
        .filter(
            Registration.status == "expired",
            Registration.expired_at >= week_start,
            Registration.expired_at < tomorrow_start,
        )
        .count()
    )

    # ========================================================
    # 4. SESSIONS AT CAPACITY
    #
    # Active registrations:
    #
    # reserved
    # confirmed
    # checked_in
    #
    # Cancelled and expired registrations do not occupy
    # seats.
    # ========================================================

    active_statuses = (
        "reserved",
        "confirmed",
        "checked_in",
    )

    active_counts = (
        db.query(
            Registration.session_id,
            func.count(Registration.id).label(
                "active_count"
            ),
        )
        .filter(
            Registration.session_id.in_(
                visible_session_ids
            ),
            Registration.status.in_(
                active_statuses
            ),
        )
        .group_by(
            Registration.session_id
        )
        .all()
    )

    active_count_map = {
        session_id: active_count
        for session_id, active_count in active_counts
    }

    sessions_at_capacity = 0

    for event_session in visible_sessions:

        active_count = active_count_map.get(
            event_session.id,
            0,
        )

        if active_count >= event_session.capacity:

            sessions_at_capacity += 1

    # ========================================================
    # 5. REGISTRATIONS BY STATUS
    # ========================================================

    status_counts = (
        db.query(
            Registration.status,
            func.count(Registration.id),
        )
        .filter(
            Registration.session_id.in_(
                visible_session_ids
            )
        )
        .group_by(
            Registration.status
        )
        .all()
    )

    status_map = {
        registration_status: count
        for registration_status, count in status_counts
    }

    registrations_by_status = {
        "reserved": status_map.get(
            "reserved",
            0,
        ),

        "confirmed": status_map.get(
            "confirmed",
            0,
        ),

        "checked_in": status_map.get(
            "checked_in",
            0,
        ),

        "cancelled": status_map.get(
            "cancelled",
            0,
        ),

        "expired": status_map.get(
            "expired",
            0,
        ),
    }

    # ========================================================
    # 6. REGISTRATIONS BY SESSION
    # ========================================================

    session_registration_counts = (
        db.query(
            Registration.session_id,
            func.count(Registration.id).label(
                "registration_count"
            ),
        )
        .filter(
            Registration.session_id.in_(
                visible_session_ids
            )
        )
        .group_by(
            Registration.session_id
        )
        .all()
    )

    registration_count_map = {
        session_id: registration_count
        for session_id, registration_count
        in session_registration_counts
    }

    registrations_by_session = []

    for event_session in visible_sessions:

        registrations_by_session.append(
            {
                "session_id": event_session.id,

                "session_title": (
                    event_session.title
                ),

                "capacity": (
                    event_session.capacity
                ),

                "registrations": (
                    registration_count_map.get(
                        event_session.id,
                        0,
                    )
                ),
            }
        )

    # ========================================================
    # SORT SESSION DATA
    # ========================================================

    registrations_by_session.sort(
        key=lambda item: item["registrations"],
        reverse=True,
    )

    # ========================================================
    # 7. CHECK-INS FOR LAST 14 DAYS
    # ========================================================

    daily_checkins = (
        db.query(
            func.date(
                Registration.checked_in_at
            ).label("checkin_date"),

            func.count(
                Registration.id
            ).label("checkin_count"),
        )
        .filter(
            Registration.session_id.in_(
                visible_session_ids
            ),

            Registration.status == "checked_in",

            Registration.checked_in_at >= (
                fourteen_days_start
            ),

            Registration.checked_in_at < (
                tomorrow_start
            ),
        )
        .group_by(
            func.date(
                Registration.checked_in_at
            )
        )
        .all()
    )

    # ========================================================
    # DATABASE DATE → COUNT
    # ========================================================

    checkin_map = {}

    for checkin_date, count in daily_checkins:

        if hasattr(
            checkin_date,
            "date",
        ):
            checkin_date = checkin_date.date()

        checkin_map[checkin_date] = count

    # ========================================================
    # CREATE ALL 14 DAYS
    #
    # Even days with zero check-ins are returned.
    # This is important for frontend charts.
    # ========================================================

    checkins_last_14_days = []

    for i in range(14):

        current_date = (
            fourteen_days_start
            + timedelta(days=i)
        ).date()

        checkins_last_14_days.append(
            {
                "date": current_date,

                "checked_in": checkin_map.get(
                    current_date,
                    0,
                ),
            }
        )

    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    return {
        "sessions_today": sessions_today,

        "checked_in_today": checked_in_today,

        "expired_this_week": expired_this_week,

        "sessions_at_capacity": (
            sessions_at_capacity
        ),

        "registrations_by_status": (
            registrations_by_status
        ),

        "registrations_by_session": (
            registrations_by_session
        ),

        "checkins_last_14_days": (
            checkins_last_14_days
        ),
    }

