"""SQLAlchemy models for the escolas module (schema: escolas)."""

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.common.database.base import TenantBaseModel


class Escola(TenantBaseModel):
    """Escola — unidade escolar pertencente a um tenant."""

    __tablename__ = "escola"
    __table_args__ = {"schema": "escolas"}

    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    codigo_sige: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    tipo: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="publica"
    )  # publica, privada, comparticipada
    nivel_ensino: Mapped[str] = mapped_column(
        String(100), nullable=False, server_default="primario"
    )  # primario, secundario_1ciclo, secundario_2ciclo, tecnico
    provincia: Mapped[str] = mapped_column(String(100), nullable=False)
    municipio: Mapped[str] = mapped_column(String(100), nullable=False)
    comuna: Mapped[str | None] = mapped_column(String(100), nullable=True)
    endereco: Mapped[str | None] = mapped_column(Text, nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    anos_letivos: Mapped[list["AnoLetivo"]] = relationship(back_populates="escola", cascade="all, delete-orphan")
    infraestruturas: Mapped[list["Infraestrutura"]] = relationship(
        back_populates="escola", cascade="all, delete-orphan"
    )
    configuracao: Mapped["ConfiguracaoEscola | None"] = relationship(back_populates="escola", uselist=False)


class AnoLetivo(TenantBaseModel):
    """Ano letivo de uma escola."""

    __tablename__ = "ano_letivo"
    __table_args__ = {"schema": "escolas"}

    escola_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("escolas.escola.id"),
        nullable=False,
        index=True,
    )
    ano: Mapped[int] = mapped_column(Integer, nullable=False)  # ex: 2026
    designacao: Mapped[str] = mapped_column(String(50), nullable=False)  # ex: "2026/2027"
    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[date] = mapped_column(Date, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    escola: Mapped["Escola"] = relationship(back_populates="anos_letivos")


class Infraestrutura(TenantBaseModel):
    """Infraestrutura da escola (sala, laboratório, etc.)."""

    __tablename__ = "infraestrutura"
    __table_args__ = {"schema": "escolas"}

    escola_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("escolas.escola.id"),
        nullable=False,
        index=True,
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="sala_aula"
    )  # sala_aula, laboratorio, biblioteca, quadra, cantina, administrativo
    capacidade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estado: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default="operacional"
    )  # operacional, em_reparacao, inoperacional
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    escola: Mapped["Escola"] = relationship(back_populates="infraestruturas")


class ConfiguracaoEscola(TenantBaseModel):
    """Configuração específica da escola (períodos, notas, etc.)."""

    __tablename__ = "configuracao_escola"
    __table_args__ = {"schema": "escolas"}

    escola_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("escolas.escola.id"),
        unique=True,
        nullable=False,
    )
    num_periodos: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("3"))
    nota_maxima: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("20"))
    nota_minima_aprovacao: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("10"))
    configuracao_extra: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, server_default=text("'{}'::jsonb")
    )

    escola: Mapped["Escola"] = relationship(back_populates="configuracao")