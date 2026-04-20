"""SQLAlchemy models for the identity module (schema: identity)."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.common.database.base import BaseModel


class Tenant(BaseModel):
    """Escola/organização — cada tenant é isolado."""

    __tablename__ = "tenant"
    __table_args__ = {"schema": "identity"}

    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        comment="Identificador URL-friendly da escola (ex: esa-luanda-1)",
    )
    estado: Mapped[str] = mapped_column(String(20), nullable=False, server_default="ativo")
    plano: Mapped[str] = mapped_column(String(50), nullable=False, server_default="basico")
    licenca_validade: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    configuracao: Mapped[dict | None] = mapped_column(JSONB, nullable=True, server_default=text("'{}'::jsonb"))

    utilizadores: Mapped[list["Utilizador"]] = relationship(back_populates="tenant")


class Papel(BaseModel):
    """Papel/role do sistema (super_admin, diretor, professor, etc.)."""

    __tablename__ = "papel"
    __table_args__ = {"schema": "identity"}

    nome: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    permissoes: Mapped[dict | None] = mapped_column(JSONB, nullable=True, server_default=text("'[]'::jsonb"))


class Utilizador(BaseModel):
    """Utilizador do sistema, vinculado a um tenant."""

    __tablename__ = "utilizador"
    __table_args__ = ({"schema": "identity"},)

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("identity.tenant.id"),
        nullable=False,
        index=True,
    )
    pessoa_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_completo: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False, server_default="local")
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    mfa_segredo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ultimo_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tenant: Mapped["Tenant"] = relationship(back_populates="utilizadores")
    papeis: Mapped[list["UtilizadorPapel"]] = relationship(back_populates="utilizador")


class UtilizadorPapel(BaseModel):
    """Associação utilizador ↔ papel com escopo."""

    __tablename__ = "utilizador_papel"
    __table_args__ = {"schema": "identity"}

    utilizador_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("identity.utilizador.id"),
        nullable=False,
    )
    papel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("identity.papel.id"),
        nullable=False,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("identity.tenant.id"),
        nullable=False,
    )
    escopo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    utilizador: Mapped["Utilizador"] = relationship(back_populates="papeis")
    papel: Mapped["Papel"] = relationship()
