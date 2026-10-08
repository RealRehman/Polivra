from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import UserResponse
from app.security.rbac import require_role
from app.services.user_service import list_organization_users

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