"""Pydantic DTOs for the identity API."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# --- Auth ---
class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
    tenant_id: uuid.UUID


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


# --- Utilizador ---
class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=128)
    nome_completo: str = Field(min_length=1, max_length=255)
    email: str | None = None
    papel: str = Field(default="professor")


class UpdateUserRequest(BaseModel):
    nome_completo: str | None = None
    email: str | None = None
    ativo: bool | None = None


class UserResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    username: str
    nome_completo: str
    email: str | None
    ativo: bool
    papeis: list[str]
    ultimo_login: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    total: int
    offset: int
    limit: int
    items: list[UserResponse]


# --- Papel ---
class PapelResponse(BaseModel):
    id: uuid.UUID
    nome: str
    descricao: str | None

    model_config = {"from_attributes": True}
