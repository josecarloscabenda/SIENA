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

class CreateInfraestruturaRequest(BaseModel):
    nome: str = Field(min_length=2, max_length=255)
    tipo: str = Field(default="sala_aula", pattern="^(sala_aula|laboratorio|biblioteca|quadra|cantina|administrativo)$")
    capacidade: int | None = Field(default=None, ge=0)
    estado: str = Field(default="operacional", pattern="^(operacional|em_reparacao|inoperacional)$")
    observacoes: str | None = None


class UpdateInfraestruturaRequest(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=255)
    tipo: str | None = Field(default=None, pattern="^(sala_aula|laboratorio|biblioteca|quadra|cantina|administrativo)$")
    capacidade: int | None = Field(default=None, ge=0)
    estado: str | None = Field(default=None, pattern="^(operacional|em_reparacao|inoperacional)$")
    observacoes: str | None = None


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


# --- Criar Escola com Tenant (super_admin) ---

class DiretorPessoaData(BaseModel):
    """Dados pessoais do diretor (Pessoa)."""
    nome_completo: str = Field(min_length=2, max_length=255)
    bi_identificacao: str = Field(min_length=5, max_length=50)
    dt_nascimento: date
    sexo: str = Field(pattern="^(M|F)$")
    nacionalidade: str = Field(default="Angolana", max_length=100)
    morada: str | None = None
    telefone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)


class DiretorUserData(BaseModel):
    """Credenciais de acesso do diretor (Utilizador)."""
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=6, max_length=128)


class CreateEscolaWithTenantRequest(BaseModel):
    # Escola
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
    # Diretor — nested objects
    diretor_pessoa: DiretorPessoaData
    diretor_user: DiretorUserData


class DiretorResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    username: str
    nome_completo: str
    email: str | None


class PessoaSimpleResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    nome_completo: str
    bi_identificacao: str
    sexo: str


class CreateEscolaWithTenantResponse(BaseModel):
    tenant_id: uuid.UUID
    escola: EscolaResponse
    diretor: DiretorResponse
    pessoa: PessoaSimpleResponse


# --- Lookup (dropdowns) ---

class AnoLetivoLookupItem(BaseModel):
    id: uuid.UUID
    designacao: str
    ano: int
    ativo: bool
    escola_id: uuid.UUID


class EscolaLookupItem(BaseModel):
    id: uuid.UUID
    nome: str
    provincia: str
    municipio: str