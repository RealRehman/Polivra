
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import Organization


def get_organization_by_slug(
    db: Session,
    slug: str,
) -> Organization | None:
    statement = select(Organization).where(
        Organization.slug == slug
    )
    return db.scalar(statement)


def get_organization_by_id(
    db: Session,
    organization_id: UUID,
) -> Organization | None:
    statement = select(Organization).where(
        Organization.id == organization_id
    )
    return db.scalar(statement)
