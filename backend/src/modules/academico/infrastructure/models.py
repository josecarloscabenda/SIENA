"""SQLAlchemy models for the academico module (schema: academico)."""

import uuid
from datetime import date, time

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.common.database.base import TenantBaseModel


class Curriculo(TenantBaseModel):
    """Currículo — definição de plano curricular por classe e ano letivo."""

    __tablename__ = "curriculo"
    __table_args__ = {"schema": "academico"}

    nivel: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="primario, secundario_1ciclo, etc."
    )
    classe: Mapped[str] = mapped_column(String(10), nullable=False)
    ano_letivo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("escolas.ano_letivo.id"),
        nullable=False,
        index=True,
    )
    carga_horaria_total: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Horas semanais"
    )

    disciplinas: Mapped[list["Disciplina"]] = relationship(
        back_populates="curriculo", cascade="all, delete-orphan"
    )


class Disciplina(TenantBaseModel):
    """Disciplina — componente curricular."""

    __tablename__ = "disciplina"
    __table_args__ = (
        UniqueConstraint("tenant_id", "codigo", name="uq_disciplina_tenant_codigo"),
        {"schema": "academico"},
    )

    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    codigo: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Único por tenant"
    )
    curriculo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academico.curriculo.id"),
        nullable=False,
        index=True,
    )
    carga_horaria_semanal: Mapped[int] = mapped_column(Integer, nullable=False)

    curriculo: Mapped["Curriculo"] = relationship(back_populates="disciplinas")


class Turma(TenantBaseModel):
    """Turma — agrupamento de alunos."""

    __tablename__ = "turma"
    __table_args__ = {"schema": "academico"}

    nome: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="7.ª-A, 10.ª-B, etc."
    )
    classe: Mapped[str] = mapped_column(String(10), nullable=False)
    turno: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="matutino, vespertino, nocturno"
    )
    ano_letivo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("escolas.ano_letivo.id"),
        nullable=False,
        index=True,
    )
    capacidade_max: Mapped[int] = mapped_column(Integer, nullable=False)
    professor_regente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("directory.professor.id"),
        nullable=False,
        index=True,
    )
    sala: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="Sala/infraestrutura"
    )

    horarios: Mapped[list["HorarioAula"]] = relationship(
        back_populates="turma", cascade="all, delete-orphan"
    )


class HorarioAula(TenantBaseModel):
    """Horário de aula — bloco de tempo semanal."""

    __tablename__ = "horario_aula"
    __table_args__ = {"schema": "academico"}

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
    professor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("directory.professor.id"),
        nullable=False,
        index=True,
    )
    dia_semana: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="segunda, terca, quarta, quinta, sexta, sabado",
    )
    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    hora_fim: Mapped[time] = mapped_column(Time, nullable=False)

    turma: Mapped["Turma"] = relationship(back_populates="horarios")


class DiarioClasse(TenantBaseModel):
    """Diário de classe — registo de aula leccionada."""

    __tablename__ = "diario_classe"
    __table_args__ = {"schema": "academico"}

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
    professor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("directory.professor.id"),
        nullable=False,
        index=True,
    )
    data_aula: Mapped[date] = mapped_column(Date, nullable=False)
    conteudo: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Conteúdo leccionado"
    )
    sumario: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Sumário da aula"
    )
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    presencas: Mapped[list["PresencaDiario"]] = relationship(
        back_populates="diario", cascade="all, delete-orphan"
    )


class PresencaDiario(TenantBaseModel):
    """Presença de aluno num registo de diário de classe."""

    __tablename__ = "presenca_diario"
    __table_args__ = {"schema": "academico"}

    diario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("academico.diario_classe.id"),
        nullable=False,
        index=True,
    )
    aluno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("directory.aluno.id"),
        nullable=False,
        index=True,
    )
    presente: Mapped[bool] = mapped_column(Boolean, nullable=False)
    justificativa: Mapped[str | None] = mapped_column(Text, nullable=True)

    diario: Mapped["DiarioClasse"] = relationship(back_populates="presencas")
