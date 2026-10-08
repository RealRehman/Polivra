from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import CreateUserRequest, UserResponse
from app.security.rbac import require_role

from uuid import UUID

from app.services.user_service import (
    create_organization_user,
    deactivate_organization_user,
    list_organization_users,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "",
    response_model=list[UserResponse],
)
def list_users(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> list[UserResponse]:
    users = list_organization_users(
        db,
        current_user.organization_id,
    )

    return [
        UserResponse.model_validate(user, from_attributes=True)
        for user in users
    ]


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: CreateUserRequest,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> UserResponse:
    user = create_organization_user(
        db,
        current_user.organization_id,
        user_data,
    )

    return UserResponse.model_validate(
        user,
        from_attributes=True,
    )

@router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
)
def deactivate_user(
    user_id: UUID,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> UserResponse:
    user = deactivate_organization_user(
        db,
        user_id,
        current_user.organization_id,
    )

    return UserResponse.model_validate(
        user,
        from_attributes=True,
    )