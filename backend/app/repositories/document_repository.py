
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.user import User


def get_document_by_id_and_organization(
    db: Session,
    document_id: UUID,
    organization_id: UUID,
    *,
    published_only: bool = False,
) -> Document | None:
    statement = select(Document).where(
        Document.id == document_id,
        Document.organization_id == organization_id,
        Document.archived_at.is_(None),
    )

    if published_only:
        statement = statement.where(Document.status == "published")

    return db.scalar(statement)


def get_documents_by_organization(
    db: Session,
    organization_id: UUID,
    *,
    published_only: bool = False,
) -> list[Document]:
    statement = select(Document).where(
        Document.organization_id == organization_id,
        Document.archived_at.is_(None),
    )

    if published_only:
        statement = statement.where(Document.status == "published")

    statement = statement.order_by(Document.created_at.desc())
    return list(db.scalars(statement).all())
