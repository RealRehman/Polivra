from pydantic import BaseModel, Field
from uuid import UUID


class LoginRequest(BaseModel):
    organization_slug: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    organization_id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool

    model_config = {
        "from_attributes": True,
    }

class CreateUserRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    role: str = Field(min_length=1, max_length=50)