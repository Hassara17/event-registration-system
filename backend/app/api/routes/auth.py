from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    TokenResponse,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
):
    # --------------------------------------------------------
    # Check if email already exists
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Create new user
    # --------------------------------------------------------

    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(
            user_data.password
        ),
        role="attendee",
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


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    db: Annotated[Session, Depends(get_db)],
):
    # --------------------------------------------------------
    # Find user by email
    # --------------------------------------------------------

    user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # --------------------------------------------------------
    # Verify password
    # --------------------------------------------------------

    if not verify_password(
        form_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # --------------------------------------------------------
    # Check active account
    # --------------------------------------------------------

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # --------------------------------------------------------
    # Create JWT access token
    # --------------------------------------------------------

    access_token = create_access_token(
        user_id=user.id,
        role=user.role,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


# ============================================================
# GET CURRENT USER
# ============================================================

@router.get(
    "/me",
)
def get_me(
    current_user: User = Depends(
        get_current_user
    ),
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }


# ============================================================
# ORGANIZER TEST
# ============================================================

@router.get(
    "/organizer-test",
)
def organizer_test(
    current_user: User = Depends(
        get_current_user
    ),
):
    if current_user.role != "organizer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organizer role required",
        )

    return {
        "message": "Organizer access granted",
        "user_id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
    }