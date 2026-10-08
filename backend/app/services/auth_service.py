from sqlalchemy.orm import Session

from app.repositories.organization_repository import (
    get_organization_by_slug,
)
from app.repositories.user_repository import (
    get_user_by_email_and_organization,
)
from app.schemas.auth import LoginRequest
from app.security.jwt import create_access_token
from app.security.password import verify_password


class AuthenticationError(Exception):
    pass


def authenticate_user(
    db: Session,
    login_data: LoginRequest,
) -> str:
    organization = get_organization_by_slug(
        db,
        login_data.organization_slug,
    )

    if organization is None:
        raise AuthenticationError("Invalid credentials")

    user = get_user_by_email_and_organization(
        db,
        login_data.email.strip().lower(),
        organization.id,
    )

    if user is None:
        raise AuthenticationError("Invalid credentials")

    if not user.is_active:
        raise AuthenticationError("Invalid credentials")

    if not verify_password(
        login_data.password,
        user.password_hash,
    ):
        raise AuthenticationError("Invalid credentials")

    return create_access_token(
        user_id=str(user.id),
        organization_id=str(user.organization_id),
    )