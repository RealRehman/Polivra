
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.repositories.organization_repository import get_organization_by_id


def update_organization_name(
    db: Session,
    organization_id: UUID,
    name: str,
) -> Organization:
    organization = get_organization_by_id(db, organization_id)

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    organization.name = name.strip()

    db.commit()
    db.refresh(organization)

    return organization
