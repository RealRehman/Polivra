from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import get_users_by_organization


def list_organization_users(
    db: Session,
    organization_id: UUID,
) -> list[User]:
    return get_users_by_organization(
        db,
        organization_id,
    )