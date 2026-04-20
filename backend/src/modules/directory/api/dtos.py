"""Pydantic DTOs for the directory module."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
# Pessoa
# ──────────────────────────────────────────────

class PessoaBase(BaseModel):
    nome_completo: str = Field(min_length=2, max_length=255)
    bi_identificacao: str = Field(min_length=1, max_length=50)
    dt_nascimento: date
    sexo: str = Field(pattern="^[MF]$")
    nacionalidade: str = Field(default="Angolana", max_length=100)
    morada: str | None = None
    telefone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    foto_url: str | None = Field(default=None, max_length=500)


class PessoaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    nome_completo: str
    bi_identificacao: str
    dt_nascimento: date
    sexo: str
    nacionalidade: str
    morada: str | None
    telefone: str | None
    email: str | None
    foto_url: str | None
    created_at: datetime


# ──────────────────────────────────────────────
# Aluno
# ──────────────────────────────────────────────

class CreateAlunoRequest(PessoaBase):
    """Cria pessoa + aluno numa única operação."""
    n_processo: str = Field(min_length=1, max_length=50)
    ano_ingresso: int = Field(ge=2000, le=2050)
    necessidades_especiais: bool = False
    status: str = Field(
        default="ativo",
        pattern="^(ativo|transferido|desistente|concluinte)$",
    )


class UpdateAlunoRequest(BaseModel):
    # Dados pessoa (opcionais)
    nome_completo: str | None = Field(default=None, min_length=2, max_length=255)
    bi_identificacao: str | None = Field(default=None, min_length=1, max_length=50)
    dt_nascimento: date | None = None
    sexo: str | None = Field(default=None, pattern="^[MF]$")
    nacionalidade: str | None = Field(default=None, max_length=100)
    morada: str | None = None
    telefone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    foto_url: str | None = Field(default=None, max_length=500)
    # Dados aluno (opcionais)
    n_processo: str | None = Field(default=None, min_length=1, max_length=50)
    necessidades_especiais: bool | None = None
    status: str | None = Field(
        default=None,
        pattern="^(ativo|transferido|desistente|concluinte)$",
    )


class AlunoResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    pessoa_id: uuid.UUID
    n_processo: str
    ano_ingresso: int
    necessidades_especiais: bool
    status: str
    created_at: datetime
    pessoa: PessoaResponse


class AlunoDetailResponse(AlunoResponse):
    vinculos: list["VinculoResponse"] = []


class AlunoListResponse(BaseModel):
    total: int
    offset: int
    limit: int
    items: list[AlunoResponse]


# ──────────────────────────────────────────────
# Professor
# ──────────────────────────────────────────────

class CreateProfessorRequest(PessoaBase):
    """Cria pessoa + professor numa única operação."""
    codigo_funcional: str = Field(min_length=1, max_length=50)
    especialidade: str = Field(min_length=1, max_length=100)
    carga_horaria_semanal: int = Field(ge=1, le=60)
    tipo_contrato: str = Field(
        default="contrato",
        pattern="^(efetivo|contrato|substituto)$",
    )
    nivel_academico: str | None = Field(default=None, max_length=100)


class UpdateProfessorRequest(BaseModel):
    nome_completo: str | None = Field(default=None, min_length=2, max_length=255)
    bi_identificacao: str | None = Field(default=None, min_length=1, max_length=50)
    dt_nascimento: date | None = None
    sexo: str | None = Field(default=None, pattern="^[MF]$")
    nacionalidade: str | None = Field(default=None, max_length=100)
    morada: str | None = None
    telefone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    foto_url: str | None = Field(default=None, max_length=500)
    codigo_funcional: str | None = Field(default=None, min_length=1, max_length=50)
    especialidade: str | None = Field(default=None, min_length=1, max_length=100)
    carga_horaria_semanal: int | None = Field(default=None, ge=1, le=60)
    tipo_contrato: str | None = Field(
        default=None,
        pattern="^(efetivo|contrato|substituto)$",
    )
    nivel_academico: str | None = Field(default=None, max_length=100)


class ProfessorResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    pessoa_id: uuid.UUID
    codigo_funcional: str
    especialidade: str
    carga_horaria_semanal: int
    tipo_contrato: str
    nivel_academico: str | None
    created_at: datetime
    pessoa: PessoaResponse


class ProfessorListResponse(BaseModel):
    total: int
    offset: int
    limit: int
    items: list[ProfessorResponse]


# ──────────────────────────────────────────────
# Encarregado
# ──────────────────────────────────────────────

class CreateEncarregadoRequest(PessoaBase):
    """Cria pessoa + encarregado numa única operação."""
    profissao: str | None = Field(default=None, max_length=100)
    escolaridade: str | None = Field(default=None, max_length=50)


class UpdateEncarregadoRequest(BaseModel):
    nome_completo: str | None = Field(default=None, min_length=2, max_length=255)
    bi_identificacao: str | None = Field(default=None, min_length=1, max_length=50)
    dt_nascimento: date | None = None
    sexo: str | None = Field(default=None, pattern="^[MF]$")
    nacionalidade: str | None = Field(default=None, max_length=100)
    morada: str | None = None
    telefone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    foto_url: str | None = Field(default=None, max_length=500)
    profissao: str | None = Field(default=None, max_length=100)
    escolaridade: str | None = Field(default=None, max_length=50)


class EncarregadoResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    pessoa_id: uuid.UUID
    profissao: str | None
    escolaridade: str | None
    created_at: datetime
    pessoa: PessoaResponse


class EncarregadoListResponse(BaseModel):
    total: int
    offset: int
    limit: int
    items: list[EncarregadoResponse]


# ──────────────────────────────────────────────
# Vínculo Aluno ↔ Encarregado
# ──────────────────────────────────────────────

class CreateVinculoRequest(BaseModel):
    encarregado_id: uuid.UUID
    tipo: str = Field(pattern="^(pai|mae|tutor|outro)$")
    principal: bool = False


class VinculoResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    aluno_id: uuid.UUID
    encarregado_id: uuid.UUID
    tipo: str
    principal: bool
    created_at: datetime
    encarregado: EncarregadoResponse | None = None


# ──────────────────────────────────────────────
# Lookup (para dropdowns em formulários)
# ──────────────────────────────────────────────

class AlunoLookupItem(BaseModel):
    id: uuid.UUID
    nome: str
    n_processo: str


class ProfessorLookupItem(BaseModel):
    id: uuid.UUID
    nome: str
    codigo_funcional: str
    especialidade: str


class EncarregadoLookupItem(BaseModel):
    id: uuid.UUID
    nome: str
    bi_identificacao: str
    telefone: str | None = None