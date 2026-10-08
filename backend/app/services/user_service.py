from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import get_users_by_organization
################################################################################
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import (
    get_user_by_email_and_organization,
    get_user_by_id_and_organization,
    get_users_by_organization,
)
from app.schemas.auth import CreateUserRequest
from app.security.password import hash_password



def list_organization_users(
    db: Session,
    organization_id: UUID,
) -> list[User]:
    return get_users_by_organization(
        db,
        organization_id,
    )

def create_organization_user(
    db: Session,
    organization_id,
    user_data: CreateUserRequest,
) -> User:
    email = user_data.email.strip().lower()

    existing_user = get_user_by_email_and_organization(
        db,
        email,
        organization_id,
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    user = User(
        organization_id=organization_id,
        email=email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name.strip(),
        role=user_data.role.lower(),
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def deactivate_organization_user(
    db: Session,
    user_id: UUID,
    organization_id: UUID,
) -> User:
    user = get_user_by_id_and_organization(
        db,
        user_id,
        organization_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.is_active = False

    db.commit()
    db.refresh(user)

    return user