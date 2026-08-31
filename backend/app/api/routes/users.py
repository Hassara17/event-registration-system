from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_organizer
from app.core.database import get_db
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ============================================================
# CREATE USER
# Organizer only
# ============================================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: UserCreate,
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    current_user: Annotated[
        User,
        Depends(require_organizer),
    ],
):
    # Check whether email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    # Create the new user
    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(
            user_data.password
        ),
        role=user_data.role,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
    }