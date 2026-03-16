"""SQLAlchemy models for the directory module (schema: directory)."""

import uuid
from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.common.database.base import TenantBaseModel


class Pessoa(TenantBaseModel):
    """Pessoa — registo centralizado de todas as pessoas no sistema."""

    __tablename__ = "pessoa"
    __table_args__ = (
        UniqueConstraint("tenant_id", "bi_identificacao", name="uq_pessoa_tenant_bi"),
        {"schema": "directory"},
    )

    nome_completo: Mapped[str] = mapped_column(String(255), nullable=False)
    bi_identificacao: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="BI / Cartão de Cidadão"
    )
    dt_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    sexo: Mapped[str] = mapped_column(String(1), nullable=False, comment="M, F")
    nacionalidade: Mapped[str] = mapped_column(
        String(100), nullable=False, server_default="Angolana"
    )
    morada: Mapped[str | None] = mapped_column(Text, nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    foto_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="Referência S3"
    )

    # Relationships
    aluno: Mapped["Aluno | None"] = relationship(back_populates="pessoa", uselist=False)
    professor: Mapped["Professor | None"] = relationship(back_populates="pessoa", uselist=False)
    encarregado: Mapped["Encarregado | None"] = relationship(back_populates="pessoa", uselist=False)
    funcionario: Mapped["Funcionario | None"] = relationship(back_populates="pessoa", uselist=False)


class Aluno(TenantBaseModel):
    """Aluno — dados específicos do papel de aluno."""

    __tablename__ = "aluno"
    __table_args__ = (
        UniqueConstraint("tenant_id", "n_processo", name="uq_aluno_tenant_nprocesso"),
        {"schema": "directory"},
    )

    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("directory.pessoa.id"),
        nullable=False,
        index=True,
    )
    n_processo: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Número de processo"
    )
    ano_ingresso: Mapped[int] = mapped_column(Integer, nullable=False)
    necessidades_especiais: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="ativo",
        comment="ativo, transferido, desistente, concluinte",
    )

    pessoa: Mapped["Pessoa"] = relationship(back_populates="aluno")
    vinculos: Mapped[list["VinculoAlunoEncarregado"]] = relationship(
        back_populates="aluno", cascade="all, delete-orphan"
    )


class Professor(TenantBaseModel):
    """Professor — dados específicos do papel de professor."""

    __tablename__ = "professor"
    __table_args__ = {"schema": "directory"}

    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("directory.pessoa.id"),
        nullable=False,
        index=True,
    )
    codigo_funcional: Mapped[str] = mapped_column(String(50), nullable=False)
    especialidade: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Área de formação"
    )
    carga_horaria_semanal: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo_contrato: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="contrato",
        comment="efetivo, contrato, substituto",
    )
    nivel_academico: Mapped[str | None] = mapped_column(String(100), nullable=True)

    pessoa: Mapped["Pessoa"] = relationship(back_populates="professor")


class Encarregado(TenantBaseModel):
    """Encarregado — dados específicos do papel de encarregado de educação."""

    __tablename__ = "encarregado"
    __table_args__ = {"schema": "directory"}

    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("directory.pessoa.id"),
        nullable=False,
        index=True,
    )
    profissao: Mapped[str | None] = mapped_column(String(100), nullable=True)
    escolaridade: Mapped[str | None] = mapped_column(String(50), nullable=True)

    pessoa: Mapped["Pessoa"] = relationship(back_populates="encarregado")
    vinculos: Mapped[list["VinculoAlunoEncarregado"]] = relationship(
        back_populates="encarregado", cascade="all, delete-orphan"
    )


class Funcionario(TenantBaseModel):
    """Funcionário — pessoal administrativo e auxiliar."""

    __tablename__ = "funcionario"
    __table_args__ = {"schema": "directory"}

    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("directory.pessoa.id"),
        nullable=False,
        index=True,
    )
    cargo: Mapped[str] = mapped_column(String(100), nullable=False)
    departamento: Mapped[str] = mapped_column(String(100), nullable=False)
    data_admissao: Mapped[date] = mapped_column(Date, nullable=False)
    tipo_contrato: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="contrato",
        comment="efetivo, contrato",
    )

    pessoa: Mapped["Pessoa"] = relationship(back_populates="funcionario")


class VinculoAlunoEncarregado(TenantBaseModel):
    """Vínculo entre aluno e encarregado de educação."""

    __tablename__ = "vinculo_aluno_encarregado"
    __table_args__ = (
        UniqueConstraint("aluno_id", "encarregado_id", name="uq_vinculo_aluno_enc"),
        {"schema": "directory"},
    )

    aluno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("directory.aluno.id"),
        nullable=False,
        index=True,
    )
    encarregado_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("directory.encarregado.id"),
        nullable=False,
        index=True,
    )
    tipo: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="pai, mae, tutor, outro"
    )
    principal: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false", comment="Encarregado principal"
    )

    aluno: Mapped["Aluno"] = relationship(back_populates="vinculos")
    encarregado: Mapped["Encarregado"] = relationship(back_populates="vinculos")