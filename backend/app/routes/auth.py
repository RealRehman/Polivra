from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# from app.security.dependencies import get_current_user
from app.models.user import User
from app.security.dependencies import get_current_user

from app.security.rbac import require_role

from app.database.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import (
    AuthenticationError,
    authenticate_user,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    try:
        access_token = authenticate_user(
            db,
            login_data,
        )
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return TokenResponse(
        access_token=access_token,
    )

@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user),
) -> dict:
    return {
        "user_id": str(current_user.id),
        "organization_id": str(current_user.organization_id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }
@router.get("/admin-test")
def admin_test(
    current_user: User = Depends(require_role("admin")),
) -> dict:
    return {
        "message": "Admin access granted",
        "user_id": str(current_user.id),
        "role": current_user.role,
    }