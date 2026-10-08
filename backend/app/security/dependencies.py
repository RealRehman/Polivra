from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.repositories.user_repository import get_user_by_email_and_organization
from app.security.jwt import decode_access_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_access_token(credentials.credentials)

        user_id = payload.get("sub")
        organization_id = payload.get("org")

        if not user_id or not organization_id:
            raise ValueError("Missing required token claims")

        user = db.get(User, user_id)

        if user is None:
            raise ValueError("User not found")

        if str(user.organization_id) != organization_id:
            raise ValueError("Organization mismatch")

        if not user.is_active:
            raise ValueError("User is inactive")

        return user

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )