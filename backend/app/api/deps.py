from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.models.session import Session as EventSession


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# ============================================================
# GET CURRENT USER
# ============================================================

def get_current_user(
    token: Annotated[
        str,
        Depends(oauth2_scheme),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    try:
        payload = decode_access_token(token)

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (
        JWTError,
        ValueError,
        TypeError,
    ):
        raise credentials_exception

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


# ============================================================
# REQUIRE SPECIFIC ROLE
# ============================================================

def require_role(required_role: str):

    def role_checker(
        current_user: Annotated[
            User,
            Depends(get_current_user),
        ],
    ) -> User:

        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{required_role} role required",
            )

        return current_user

    return role_checker


# ============================================================
# REQUIRE ORGANIZER
# ============================================================

def require_organizer(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
) -> User:

    if current_user.role != "organizer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organizer role required",
        )

    return current_user


# ============================================================
# CHECK SESSION ACCESS
# ============================================================
#
# Organizer:
#     Can access every session.
#
# Check-in staff:
#     Can access only sessions assigned to them.
#
# Attendee:
#     Cannot use staff/organizer session-management actions.
#
# ============================================================

def require_session_access(
    session_id: int,
    current_user: User,
    db: Session,
) -> EventSession:

    session = (
        db.query(EventSession)
        .filter(
            EventSession.id == session_id
        )
        .first()
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # --------------------------------------------------------
    # ORGANIZER
    # --------------------------------------------------------

    if current_user.role == "organizer":
        return session

    # --------------------------------------------------------
    # CHECK-IN STAFF
    # --------------------------------------------------------

    if current_user.role == "checkin_staff":

        assigned = any(
            staff.id == current_user.id
            for staff in session.assigned_staff
        )

        if not assigned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You are not assigned to this session"
                ),
            )

        return session

    # --------------------------------------------------------
    # ALL OTHER ROLES
    # --------------------------------------------------------

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have access to this session",
    )