
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.organization import OrganizationResponse

from app.database.session import get_db
from app.models.user import User
from app.repositories.organization_repository import get_organization_by_id
from app.security.dependencies import get_current_user

from app.schemas.organization import (
    OrganizationResponse,
    OrganizationUpdateRequest,
)
from app.security.rbac import require_role
from app.services.organization_service import update_organization_name

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("/me", response_model=OrganizationResponse)
def get_my_organization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrganizationResponse:
    organization = get_organization_by_id(
        db,
        current_user.organization_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    return OrganizationResponse.model_validate(
        organization,
        from_attributes=True,
    )
    

@router.patch("/me", response_model=OrganizationResponse)
def update_my_organization(
    update_data: OrganizationUpdateRequest,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> OrganizationResponse:
    organization = update_organization_name(
        db,
        current_user.organization_id,
        update_data.name,
    )

    return OrganizationResponse.model_validate(
        organization,
        from_attributes=True,
    )

