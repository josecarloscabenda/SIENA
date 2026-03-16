"""SQLAlchemy models for the enrollment module (schema: enrollment)."""

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.common.database.base import TenantBaseModel


class Matricula(TenantBaseModel):
    """Matrícula — pedido de inscrição de aluno num ano letivo."""

    __tablename__ = "matricula"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "aluno_id", "ano_letivo_id",
            name="uq_matricula_tenant_aluno_ano",
        ),
        {"schema": "enrollment"},
    )

    aluno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("directory.aluno.id"),
        nullable=False,
        index=True,
    )
    ano_letivo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("escolas.ano_letivo.id"),
        nullable=False,
        index=True,
    )
    classe: Mapped[str] = mapped_column(
        String(10), nullable=False, comment="1.ª, 7.ª, 10.ª, etc."
    )
    turno: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="matutino",
        comment="matutino, vespertino, nocturno",
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="pendente",
        comment="pendente, aprovada, rejeitada, cancelada",
    )
    data_pedido: Mapped[date] = mapped_column(Date, nullable=False)
    data_aprovacao: Mapped[date | None] = mapped_column(Date, nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    alocacao: Mapped["AlocacaoTurma | None"] = relationship(
        back_populates="matricula", uselist=False
    )
    documentos: Mapped[list["DocumentoMatricula"]] = relationship(
        back_populates="matricula", cascade="all, delete-orphan"
    )


class AlocacaoTurma(TenantBaseModel):
    """Alocação de aluno matriculado a uma turma específica."""

    __tablename__ = "alocacao_turma"
    __table_args__ = {"schema": "enrollment"}

    matricula_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enrollment.matricula.id"),
        nullable=False,
        index=True,
    )
    turma_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="FK para academico.turma (cross-schema, sem constraint)",
    )
    data_alocacao: Mapped[date] = mapped_column(Date, nullable=False)

    matricula: Mapped["Matricula"] = relationship(back_populates="alocacao")


class Transferencia(TenantBaseModel):
    """Transferência de aluno entre escolas."""

    __tablename__ = "transferencia"
    __table_args__ = {"schema": "enrollment"}

    aluno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("directory.aluno.id"),
        nullable=False,
        index=True,
    )
    escola_origem_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("escolas.escola.id"),
        nullable=False,
    )
    escola_destino_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("escolas.escola.id"),
        nullable=False,
    )
    data_pedido: Mapped[date] = mapped_column(Date, nullable=False)
    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="pendente",
        comment="pendente, aprovada, rejeitada, cancelada",
    )
    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    documentos_url: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="Array de URLs S3"
    )


class DocumentoMatricula(TenantBaseModel):
    """Documento associado a uma matrícula (BI, atestado, foto, etc.)."""

    __tablename__ = "documento_matricula"
    __table_args__ = {"schema": "enrollment"}

    matricula_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enrollment.matricula.id"),
        nullable=False,
        index=True,
    )
    tipo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="cartao_cidadao, atestado_vacinacao, foto, etc.",
    )
    url: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="Referência S3"
    )
    verificado: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )

    matricula: Mapped["Matricula"] = relationship(back_populates="documentos")