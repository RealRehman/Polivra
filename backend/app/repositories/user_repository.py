from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    statement = select(User).where(User.email == email)
    return db.scalar(statement)


def get_user_by_email_and_organization(
    db: Session,
    email: str,
    organization_id,
) -> User | None:
    statement = select(User).where(
        User.email == email,
        User.organization_id == organization_id,
    )

    return db.scalar(statement)


def get_users_by_organization(
    db: Session,
    organization_id: UUID,
) -> list[User]:
    statement = select(User).where(
        User.organization_id == organization_id
    ).order_by(User.created_at)

    return list(db.scalars(statement).all())