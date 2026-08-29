from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, require_role
from app.models.user import User


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.get("/me")
def get_me(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }


@router.get("/organizer-test")
def organizer_test(
    current_user: Annotated[
        User,
        Depends(require_role("organizer")),
    ],
):
    return {
        "message": "Organizer access granted",
        "user": current_user.email,
        "role": current_user.role,
    }