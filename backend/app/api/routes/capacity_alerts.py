from fastapi import (
    APIRouter,
    Depends,
)

from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_user,
    get_db,
    require_role,
)

from app.models.user import User

from app.schemas.capacity_alert import (
    CapacityAlertResponse,
)

from app.services.capacity_alert_service import (
    get_capacity_alerts,
    dismiss_capacity_alert,
)


router = APIRouter(
    prefix="/capacity-alerts",
    tags=["Capacity Alerts"],
)


# ============================================================
# GET ACTIVE CAPACITY ALERTS
# ============================================================

@router.get(
    "",
    response_model=list[CapacityAlertResponse],
)
def get_capacity_alerts_endpoint(
    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_role("organizer")
    ),
):
    return get_capacity_alerts(
        db=db,
        organizer_id=current_user.id,
    )


# ============================================================
# DISMISS CAPACITY ALERT
# ============================================================

@router.post(
    "/session/{session_id}/dismiss",
    response_model=CapacityAlertResponse,
)
def dismiss_capacity_alert_endpoint(
    session_id: int,

    db: Session = Depends(get_db),

    current_user: User = Depends(
        require_role("organizer")
    ),
):
    return dismiss_capacity_alert(
        db=db,
        session_id=session_id,
        organizer_id=current_user.id,
    )