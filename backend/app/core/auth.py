from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User


# =========================
# JWT Bearer Authentication
# =========================

security = HTTPBearer()


# =========================
# Get Current User
# =========================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    # Get JWT token from Authorization header
    token = credentials.credentials

    # Decode JWT token
    payload = decode_access_token(token)

    if payload is None:
        raise credentials_exception

    # Get user ID from token
    user_id = payload.get("sub")

    if user_id is None:
        raise credentials_exception

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise credentials_exception

    # Find user in database
    user = db.get(User, user_id)

    if user is None:
        raise credentials_exception

    # Check whether user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return user