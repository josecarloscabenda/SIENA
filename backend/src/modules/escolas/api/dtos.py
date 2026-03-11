"""Pydantic DTOs for the escolas module."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


# --- Escola ---

class CreateEscolaRequest(BaseModel):
    nome: str = Field(min_length=2, max_length=255)
    codigo_sige: str | None = Field(default=None, max_length=50)
    tipo: str = Field(default="publica", pattern="^(publica|privada|comparticipada)$")
    nivel_ensino: str = Field(
        default="primario",
        pattern="^(primario|secundario_1ciclo|secundario_2ciclo|tecnico)$",
    )
    provincia: str = Field(min_length=2, max_length=100)
    municipio: str = Field(min_length=2, max_length=100)
    comuna: str | None = Field(default=None, max_length=100)
    endereco: str | None = None
    telefone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    latitude: float | None = None
    longitude: float | None = None


class UpdateEscolaRequest(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=255)
    codigo_sige: str | None = Field(default=None, max_length=50)
    tipo: str | None = Field(default=None, pattern="^(publica|privada|comparticipada)$")
    nivel_ensino: str | None = Field(
        default=None,
        pattern="^(primario|secundario_1ciclo|secundario_2ciclo|tecnico)$",
    )
    provincia: str | None = Field(default=None, min_length=2, max_length=100)
    municipio: str | None = Field(default=None, min_length=2, max_length=100)
    comuna: str | None = Field(default=None, max_length=100)
    endereco: str | None = None
    telefone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    latitude: float | None = None
    longitude: float | None = None
    ativa: bool | None = None


class EscolaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    nome: str
    codigo_sige: str | None
    tipo: str
    nivel_ensino: str
    provincia: str
    municipio: str
    comuna: str | None
    endereco: str | None
    telefone: str | None
    email: str | None
    latitude: float | None
    longitude: float | None
    ativa: bool
    created_at: datetime


class EscolaDetailResponse(EscolaResponse):
    anos_letivos: list["AnoLetivoResponse"] = []
    infraestruturas: list["InfraestruturaResponse"] = []
    configuracao: "ConfiguracaoEscolaResponse | None" = None


class EscolaListResponse(BaseModel):
    total: int
    offset: int
    limit: int
    items: list[EscolaResponse]


# --- Ano Letivo ---

class CreateAnoLetivoRequest(BaseModel):
    ano: int = Field(ge=2020, le=2050)
    designacao: str = Field(min_length=3, max_length=50)
    data_inicio: date
    data_fim: date


class AnoLetivoResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    escola_id: uuid.UUID
    ano: int
    designacao: str
    data_inicio: date
    data_fim: date
    ativo: bool
    created_at: datetime


# --- Infraestrutura ---

class InfraestruturaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    escola_id: uuid.UUID
    nome: str
    tipo: str
    capacidade: int | None
    estado: str
    observacoes: str | None
    created_at: datetime


# --- Configuração ---

class ConfiguracaoEscolaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    escola_id: uuid.UUID
    num_periodos: int
    nota_maxima: int
    nota_minima_aprovacao: int
    configuracao_extra: dict | None