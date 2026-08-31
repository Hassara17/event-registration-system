from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    UploadFile,
    File,
    Response,
    status,
)

from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_user,
    get_db,
    require_role,
)

from app.models.user import User

from app.schemas.registration import (
    RegistrationCreate,
    RegistrationResponse,
    RegistrationHistoryResponse,
    RegistrationStatusResponse,
    SessionStatsResponse,
    RegistrationSearchResponse,
    BulkImportResponse,
    RegistrationHistoryItemResponse,
)

from app.services.registration_service import (
    check_in_registration,
    confirm_registration,
    create_registration,
    get_registration,
    get_registration_status,
    get_session_registrations,
    get_session_stats,
    get_user_registration_history,
    get_user_registrations,
    search_registrations,
    bulk_import_registrations,
    export_session_registrations,
    get_registration_history,
)


router = APIRouter(
    prefix="/registrations",
    tags=["Registrations"],
)


# ============================================================
# CREATE REGISTRATION
# ============================================================

@router.post(
    "",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_registration_endpoint(
    registration_data: RegistrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_registration(
        db=db,
        session_id=registration_data.session_id,
        user_id=current_user.id,
        attendee_name=registration_data.attendee_name,
        attendee_email=registration_data.attendee_email,
    )


# ============================================================
# MY ACTIVE REGISTRATIONS
# ============================================================

@router.get(
    "/my",
    response_model=list[RegistrationResponse],
)
def get_my_registrations_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_registrations(
        db=db,
        user_id=current_user.id,
    )


# ============================================================
# MY REGISTRATION HISTORY
# ============================================================

@router.get(
    "/my/history",
    response_model=list[RegistrationHistoryResponse],
)
def get_my_registration_history_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_registration_history(
        db=db,
        user_id=current_user.id,
    )


# ============================================================
# SEARCH REGISTRATIONS
# ============================================================

@router.get(
    "/search",
    response_model=RegistrationSearchResponse,
)
def search_registrations_endpoint(
    search: str | None = Query(
        default=None,
        description="Search attendee name or email",
    ),
    event_id: int | None = Query(
        default=None,
        description="Filter by event ID",
    ),
    session_id: int | None = Query(
        default=None,
        description="Filter by session ID",
    ),
    registration_status: str | None = Query(
        default=None,
        description=(
            "Filter by registration status: "
            "reserved, confirmed, checked_in, "
            "cancelled, expired"
        ),
    ),
    sort_by: str = Query(
        default="reserved_at",
        description="Sort field: reserved_at, status, session",
    ),
    sort_order: str = Query(
        default="desc",
        description="Sort direction: asc or desc",
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="Page number",
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of records per page",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return search_registrations(
        db=db,
        viewer=current_user,
        search=search,
        event_id=event_id,
        session_id=session_id,
        registration_status=registration_status,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )


# ============================================================
# BULK IMPORT REGISTRATIONS
# Organizer only
# ============================================================

@router.post(
    "/session/{session_id}/import",
    response_model=BulkImportResponse,
)
def bulk_import_registrations_endpoint(
    session_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file is required",
        )

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported",
        )

    try:
        contents = file.file.read()
        csv_content = contents.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file must be UTF-8 encoded",
        )

    return bulk_import_registrations(
        db=db,
        session_id=session_id,
        organizer_id=current_user.id,
        csv_content=csv_content,
    )


# ============================================================
# EXPORT SESSION REGISTRATIONS
# Organizer only
# ============================================================

@router.get(
    "/session/{session_id}/export",
)
def export_session_registrations_endpoint(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):
    csv_content = export_session_registrations(
        db=db,
        session_id=session_id,
        organizer_id=current_user.id,
    )

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                f'attachment; filename="session_{session_id}_checkin.csv"'
            )
        },
    )


# ============================================================
# REGISTRATION HISTORY TIMELINE
# ============================================================

@router.get(
    "/{registration_id}/history",
    response_model=list[RegistrationHistoryItemResponse],
)
def get_registration_history_endpoint(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    registration = get_registration(
        db=db,
        registration_id=registration_id,
    )

    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )

    # --------------------------------------------------------
    # ATTENDEE / REGISTRATION OWNER
    # --------------------------------------------------------

    if registration.user_id == current_user.id:
        return get_registration_history(
            db=db,
            registration_id=registration_id,
        )

    # --------------------------------------------------------
    # GET SESSION
    # --------------------------------------------------------

    event_session = registration.session

    if event_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration session not found",
        )

    # --------------------------------------------------------
    # ORGANIZER
    # --------------------------------------------------------

    if current_user.role == "organizer":
        if (
            event_session.event is not None
            and event_session.event.organizer_id
            == current_user.id
        ):
            return get_registration_history(
                db=db,
                registration_id=registration_id,
            )

    # --------------------------------------------------------
    # CHECK-IN STAFF
    # --------------------------------------------------------

    if current_user.role == "checkin_staff":
        assigned = any(
            staff.id == current_user.id
            for staff in event_session.assigned_staff
        )

        if assigned:
            return get_registration_history(
                db=db,
                registration_id=registration_id,
            )

    # --------------------------------------------------------
    # ACCESS DENIED
    # --------------------------------------------------------

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=(
            "You do not have permission "
            "to view this registration history"
        ),
    )


# ============================================================
# GET REGISTRATION
# ============================================================

@router.get(
    "/{registration_id}",
    response_model=RegistrationResponse,
)
def get_registration_endpoint(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    registration = get_registration(
        db=db,
        registration_id=registration_id,
    )

    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )

    # --------------------------------------------------------
    # USER CAN SEE OWN REGISTRATION
    # --------------------------------------------------------

    if registration.user_id == current_user.id:
        return registration

    # --------------------------------------------------------
    # ORGANIZER
    # --------------------------------------------------------

    if current_user.role == "organizer":
        session = registration.session

        if (
            session is not None
            and session.event is not None
            and session.event.organizer_id
            == current_user.id
        ):
            return registration

    # --------------------------------------------------------
    # CHECK-IN STAFF
    # --------------------------------------------------------

    if current_user.role == "checkin_staff":
        session = registration.session

        if session is not None:
            assigned = any(
                staff.id == current_user.id
                for staff in session.assigned_staff
            )

            if assigned:
                return registration

    # --------------------------------------------------------
    # ACCESS DENIED
    # --------------------------------------------------------

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=(
            "You do not have permission "
            "to view this registration"
        ),
    )


# ============================================================
# CANCEL REGISTRATION
# ============================================================

@router.post(
    "/{registration_id}/cancel",
    response_model=RegistrationResponse,
)
def cancel_registration_endpoint(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.registration_service import (
        cancel_registration,
    )

    return cancel_registration(
        db=db,
        registration_id=registration_id,
        actor_user_id=current_user.id,
    )


# ============================================================
# CONFIRM REGISTRATION
# Organizer only
# ============================================================

@router.post(
    "/{registration_id}/confirm",
    response_model=RegistrationResponse,
)
def confirm_registration_endpoint(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):
    return confirm_registration(
        db=db,
        registration_id=registration_id,
        actor_user_id=current_user.id,
    )


# ============================================================
# CHECK IN REGISTRATION
#
# Organizer:
#   Can check in registrations belonging to
#   sessions in their own events.
#
# Check-in Staff:
#   Can check in registrations only for
#   sessions assigned to them.
#
# Attendee:
#   Cannot check in.
# ============================================================

@router.post(
    "/{registration_id}/check-in",
    response_model=RegistrationResponse,
)
def check_in_registration_endpoint(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Check in a registration.

    Organizer:
        Can check in registrations from their own events.

    Check-in Staff:
        Can check in registrations only from sessions
        assigned to them.

    Attendee:
        Cannot check in.
    """

    # --------------------------------------------------------
    # GET REGISTRATION
    # --------------------------------------------------------

    registration = get_registration(
        db=db,
        registration_id=registration_id,
    )

    if registration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration not found",
        )

    # --------------------------------------------------------
    # GET SESSION
    # --------------------------------------------------------

    event_session = registration.session

    if event_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration session not found",
        )

    # --------------------------------------------------------
    # ORGANIZER
    # --------------------------------------------------------

    if current_user.role == "organizer":

        if (
            event_session.event is not None
            and event_session.event.organizer_id
            == current_user.id
        ):
            return check_in_registration(
                db=db,
                registration_id=registration_id,
                actor_user_id=current_user.id,
            )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Organizer can only check in "
                "registrations from their own events"
            ),
        )

    # --------------------------------------------------------
    # CHECK-IN STAFF
    # --------------------------------------------------------

    if current_user.role == "checkin_staff":

        assigned = any(
            staff.id == current_user.id
            for staff in event_session.assigned_staff
        )

        if not assigned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Check-in staff can only check in "
                    "registrations for assigned sessions"
                ),
            )

        # IMPORTANT:
        # The service function must NOT perform an
        # organizer ownership check for check-in staff.
        return check_in_registration(
            db=db,
            registration_id=registration_id,
            actor_user_id=current_user.id,
        )

    # --------------------------------------------------------
    # ALL OTHER ROLES
    # --------------------------------------------------------

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=(
            "You do not have permission "
            "to check in registrations"
        ),
    )


# ============================================================
# GET SESSION REGISTRATIONS
# Organizer only
# ============================================================

@router.get(
    "/session/{session_id}",
    response_model=list[RegistrationResponse],
)
def get_session_registrations_endpoint(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):
    return get_session_registrations(
        db=db,
        session_id=session_id,
        organizer_id=current_user.id,
    )


# ============================================================
# SESSION REGISTRATION STATISTICS
# Organizer only
# ============================================================

@router.get(
    "/session/{session_id}/stats",
    response_model=SessionStatsResponse,
)
def get_session_stats_endpoint(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):
    return get_session_stats(
        db=db,
        session_id=session_id,
        organizer_id=current_user.id,
    )


# ============================================================
# CURRENT USER REGISTRATION STATUS
# ============================================================

@router.get(
    "/session/{session_id}/status",
    response_model=RegistrationStatusResponse,
)
def get_registration_status_endpoint(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_registration_status(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
    )