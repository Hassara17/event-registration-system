from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_user,
    get_db,
)

from app.models.user import User

from app.schemas.dashboard import (
    DashboardResponse,
)

from app.services.dashboard_service import (
    get_dashboard,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# ============================================================
# DASHBOARD
# ============================================================

@router.get(
    "",
    response_model=DashboardResponse,
)
def get_dashboard_endpoint(
    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Return dashboard statistics.

    Organizers:
        See data for their own events.

    Check-in staff:
        See data for sessions assigned to them.
    """

    return get_dashboard(
        db=db,
        current_user=current_user,
    )