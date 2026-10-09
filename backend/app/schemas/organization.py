
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from pydantic import BaseModel, ConfigDict, Field

class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class OrganizationUpdateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)

    model_config = ConfigDict(extra="forbid")
