"""SQLAlchemy models for the avaliacoes module (schema: avaliacoes)."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.common.database.base import TenantBaseModel


class Avaliacao(TenantBaseModel):
    """Avaliação — teste, trabalho, exame ou oral."""

    __tablename__ = "avaliacao"
    __table_args__ = {"schema": "avaliacoes"}

    turma_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academico.turma.id"),
        nullable=False,
        index=True,
    )
    disciplina_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academico.disciplina.id"),
        nullable=False,
        index=True,
    )
    tipo: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="teste, trabalho, exame, oral"
    )
    periodo: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="1, 2 ou 3"
    )
    data: Mapped[date] = mapped_column(Date, nullable=False)
    peso: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Peso na média final"
    )
    nota_maxima: Mapped[int] = mapped_column(Integer, nullable=False)

    notas: Mapped[list["Nota"]] = relationship(
        back_populates="avaliacao", cascade="all, delete-orphan"
    )


class Nota(TenantBaseModel):
    """Nota de aluno numa avaliação."""

    __tablename__ = "nota"
    __table_args__ = (
        UniqueConstraint("avaliacao_id", "aluno_id", name="uq_nota_avaliacao_aluno"),
        {"schema": "avaliacoes"},
    )

    avaliacao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("avaliacoes.avaliacao.id"),
        nullable=False,
        index=True,
    )
    aluno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("directory.aluno.id"),
        nullable=False,
        index=True,
    )
    valor: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    lancado_por: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, comment="Professor que lançou"
    )
    lancado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )

    avaliacao: Mapped["Avaliacao"] = relationship(back_populates="notas")


class Falta(TenantBaseModel):
    """Falta de aluno a uma aula."""

    __tablename__ = "falta"
    __table_args__ = {"schema": "avaliacoes"}

    aluno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("directory.aluno.id"),
        nullable=False,
        index=True,
    )
    turma_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academico.turma.id"),
        nullable=False,
        index=True,
    )
    disciplina_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academico.disciplina.id"),
        nullable=False,
        index=True,
    )
    data: Mapped[date] = mapped_column(Date, nullable=False)
    tipo: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="justificada, injustificada"
    )
    justificativa: Mapped[str | None] = mapped_column(Text, nullable=True)


class RegraMedia(TenantBaseModel):
    """Regra de cálculo de média por nível/disciplina."""

    __tablename__ = "regra_media"
    __table_args__ = {"schema": "avaliacoes"}

    nivel: Mapped[str] = mapped_column(String(50), nullable=False)
    disciplina_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academico.disciplina.id"),
        nullable=True,
        index=True,
        comment="NULL = todas",
    )
    formula: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="Fórmula de cálculo"
    )
    minimo_aprovacao: Mapped[int] = mapped_column(Integer, nullable=False)
    politica_recuperacao: Mapped[str | None] = mapped_column(Text, nullable=True)


class Boletim(TenantBaseModel):
    """Boletim gerado para um aluno num período."""

    __tablename__ = "boletim"
    __table_args__ = {"schema": "avaliacoes"}

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
    periodo: Mapped[int] = mapped_column(Integer, nullable=False)
    gerado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )
    url_pdf: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="Referência S3"
    )
