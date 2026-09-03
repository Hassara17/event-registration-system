from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_user,
    get_db,
    require_role,
)

from app.models.user import User

from app.schemas.event import (
    EventCreate,
    EventResponse,
    EventUpdate,
)

from app.schemas.event_detail import EventDetailResponse
from app.schemas.event_stats import EventStatsResponse

from app.services.event_service import (
    archive_event,
    create_event,
    delete_event,
    get_event,
    get_event_detail,
    get_event_stats,
    get_events,
    restore_event,
    update_event,
)


router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


# ============================================================
# CREATE EVENT
# ============================================================

@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event_endpoint(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):
    return create_event(
        db=db,
        event_data=event_data,
        organizer_id=current_user.id,
    )


# ============================================================
# LIST EVENTS
# ============================================================

@router.get(
    "",
    response_model=list[EventResponse],
)
def list_events(
    search: str | None = Query(
        default=None,
        description="Search event title or description",
    ),

    venue: str | None = Query(
        default=None,
        description="Filter by venue",
    ),

    event_date: date | None = Query(
        default=None,
        description="Filter by event start date",
    ),

    archived: bool = Query(
        default=False,
        description=(
            "False = active events, "
            "True = archived events"
        ),
    ),

    page: int = Query(
        default=1,
        ge=1,
        description="Page number",
    ),

    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of events per page",
    ),

    sort_by: str = Query(
        default="start_date",
        description="Sort field: start_date, title, venue",
    ),

    sort_order: str = Query(
        default="asc",
        description="Sort order: asc or desc",
    ),

    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # Validate sorting
    # --------------------------------------------------------

    allowed_sort_fields = {
        "start_date",
        "title",
        "venue",
    }

    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid sort_by. Allowed values: "
                "start_date, title, venue"
            ),
        )

    if sort_order.lower() not in {
        "asc",
        "desc",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid sort_order. "
                "Allowed values: asc, desc"
            ),
        )

    # --------------------------------------------------------
    # Get events
    # --------------------------------------------------------

    return get_events(
        db=db,
        search=search,
        venue=venue,
        event_date=event_date,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order.lower(),
        archived=archived,
    )


# ============================================================
# GET EVENT DETAILS
# ============================================================

@router.get(
    "/{event_id}/details",
    response_model=EventDetailResponse,
)
def get_event_detail_endpoint(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    event_detail = get_event_detail(
        db=db,
        event_id=event_id,
        user_id=current_user.id,
    )

    if event_detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return event_detail


# ============================================================
# GET EVENT STATISTICS
# ============================================================

@router.get(
    "/{event_id}/stats",
    response_model=EventStatsResponse,
)
def get_event_stats_endpoint(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):

    event = get_event(
        db=db,
        event_id=event_id,
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    if event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only view statistics "
                "for your own events"
            ),
        )

    return get_event_stats(
        db=db,
        event_id=event_id,
        organizer_id=current_user.id,
    )


# ============================================================
# ARCHIVE EVENT
# ============================================================

@router.post(
    "/{event_id}/archive",
    response_model=EventResponse,
)
def archive_event_endpoint(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):

    event = get_event(
        db=db,
        event_id=event_id,
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    if event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only archive "
                "your own events"
            ),
        )

    return archive_event(
        db=db,
        event=event,
    )


# ============================================================
# RESTORE EVENT
# ============================================================

@router.post(
    "/{event_id}/restore",
    response_model=EventResponse,
)
def restore_event_endpoint(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):

    event = get_event(
        db=db,
        event_id=event_id,
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    if event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only restore "
                "your own events"
            ),
        )

    return restore_event(
        db=db,
        event=event,
    )


# ============================================================
# GET SINGLE EVENT
# ============================================================

@router.get(
    "/{event_id}",
    response_model=EventResponse,
)
def get_event_endpoint(
    event_id: int,
    db: Session = Depends(get_db),
):

    event = get_event(
        db=db,
        event_id=event_id,
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return event


# ============================================================
# UPDATE EVENT
# ============================================================

@router.patch(
    "/{event_id}",
    response_model=EventResponse,
)
def update_event_endpoint(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):

    event = get_event(
        db=db,
        event_id=event_id,
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    if event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only modify "
                "your own events"
            ),
        )

    return update_event(
        db=db,
        event=event,
        event_data=event_data,
    )


# ============================================================
# DELETE EVENT
# ============================================================

@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_event_endpoint(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("organizer")
    ),
):

    event = get_event(
        db=db,
        event_id=event_id,
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    if event.organizer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You can only delete "
                "your own events"
            ),
        )

    delete_event(
        db=db,
        event=event,
    )

    return None