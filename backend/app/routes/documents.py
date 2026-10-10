
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from uuid import UUID

from app.security.rbac import require_role

from fastapi import HTTPException, status

from fastapi.responses import FileResponse
from app.storage.local_storage import get_document_path

from app.services.document_service import get_organization_document

from app.database.session import get_db
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.security.dependencies import get_current_user
from app.services.document_service import (
    archive_organization_document,
    get_organization_document,
    get_organization_documents,
    publish_organization_document,
    upload_organization_document,
)

from app.services.document_service import archive_organization_document

from fastapi import File, Form, UploadFile, status

from app.schemas.document import DocumentUploadRequest
from app.services.document_service import upload_organization_document

router = APIRouter(prefix="/documents", tags=["Documents"])



@router.get("", response_model=list[DocumentResponse])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DocumentResponse]:
    documents = get_organization_documents(
        db,
        current_user.organization_id,
        published_only=current_user.role != "admin",
    )

    return [
        DocumentResponse.model_validate(document, from_attributes=True)
        for document in documents
    ]



@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    document = get_organization_document(
        db,
        document_id,
        current_user.organization_id,
        published_only=current_user.role != "admin",
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return DocumentResponse.model_validate(
        document,
        from_attributes=True,
    )


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    title: str = Form(..., min_length=2, max_length=255),
    description: str | None = Form(default=None, max_length=5000),
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    document = await upload_organization_document(
        db=db,
        organization_id=current_user.organization_id,
        uploaded_by=current_user.id,
        title=title,
        description=description,
        upload=file,
    )

    return DocumentResponse.model_validate(
        document,
        from_attributes=True,
    )

@router.get("/{document_id}/download")
def download_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FileResponse:
    document = get_organization_document(
        db,
        document_id,
        current_user.organization_id,
        published_only=current_user.role != "admin",
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    if document.archived_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
    )


    file_path = get_document_path(document.file_key)

    return FileResponse(
        path=file_path,
        media_type="application/octet-stream",
        filename=f"{document.title}",
        content_disposition_type="attachment",
    )
    

@router.patch("/{document_id}/archive", response_model=DocumentResponse)
def archive_document(
    document_id: UUID,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    document = archive_organization_document(
        db,
        document_id,
        current_user.organization_id,
    )

    return DocumentResponse.model_validate(
        document,
        from_attributes=True,
    )

@router.patch("/{document_id}/publish", response_model=DocumentResponse)
def publish_document(
    document_id: UUID,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    document = publish_organization_document(
        db,
        document_id,
        current_user.organization_id,
    )

    return DocumentResponse.model_validate(
        document,
        from_attributes=True,
    )