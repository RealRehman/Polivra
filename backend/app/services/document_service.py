
from uuid import UUID

from sqlalchemy.orm import Session

from datetime import datetime, timezone

from fastapi import UploadFile
from app.storage.local_storage import save_document
from app.storage.local_storage import delete_document_file, save_document

from app.models.document import Document
from app.repositories.document_repository import (
    get_document_by_id_and_organization,
    get_documents_by_organization,
)


def get_organization_documents(
    db: Session,
    organization_id: UUID,
) -> list[Document]:
    return get_documents_by_organization(db, organization_id)


def get_organization_document(
    db: Session,
    document_id: UUID,
    organization_id: UUID,
) -> Document | None:
    return get_document_by_id_and_organization(
        db,
        document_id,
        organization_id,
    )



async def upload_organization_document(
    db: Session,
    organization_id: UUID,
    uploaded_by: UUID,
    title: str,
    description: str | None,
    upload: UploadFile,
) -> Document:
    content_type = upload.content_type or "application/octet-stream"
    file_key, _ = await save_document(upload)

    try:
        document = Document(
            organization_id=organization_id,
            uploaded_by=uploaded_by,
            title=title.strip(),
            description=description.strip() if description else None,
            file_key=file_key,
            content_type=content_type,
            status="uploaded",
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    except Exception:
        db.rollback()

        try:
            delete_document_file(file_key)
        except OSError:
            # Preserve the original database error.
            pass

        raise



def archive_organization_document(
    db: Session,
    document_id: UUID,
    organization_id: UUID,
) -> Document:
    document = get_document_by_id_and_organization(
        db,
        document_id,
        organization_id,
    )

    if document is None:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if document.archived_at is not None:
        return document

    document.archived_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(document)

    return document

