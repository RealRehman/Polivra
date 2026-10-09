
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


from pydantic import Field


class DocumentUploadRequest(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=5000)

    model_config = ConfigDict(extra="forbid")



class DocumentResponse(BaseModel):
    id: UUID
    organization_id: UUID
    uploaded_by: UUID
    title: str
    description: str | None
    # file_key: str
    content_type: str
    status: str
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
