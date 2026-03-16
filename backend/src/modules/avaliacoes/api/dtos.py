"""Pydantic DTOs for the avaliacoes module."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


# ── Avaliação ───────────────────────────────────

class CreateAvaliacaoRequest(BaseModel):
    turma_id: uuid.UUID
    disciplina_id: uuid.UUID
    tipo: str = Field(pattern="^(teste|trabalho|exame|oral)$")
    periodo: int = Field(ge=1, le=3)
    data: date
    peso: float = Field(gt=0, le=1)
    nota_maxima: int = Field(ge=1, le=100)


class AvaliacaoResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    turma_id: uuid.UUID
    disciplina_id: uuid.UUID
    tipo: str
    periodo: int
    data: date
    peso: float
    nota_maxima: int
    created_at: datetime


class AvaliacaoDetailResponse(AvaliacaoResponse):
    notas: list["NotaResponse"] = []


class AvaliacaoListResponse(BaseModel):
    total: int
    offset: int
    limit: int
    items: list[AvaliacaoResponse]


# ── Nota ────────────────────────────────────────

class NotaInput(BaseModel):
    aluno_id: uuid.UUID
    valor: Decimal = Field(ge=0)
    observacoes: str | None = None


class LancarNotasRequest(BaseModel):
    notas: list[NotaInput] = Field(min_length=1)


class UpdateNotaRequest(BaseModel):
    valor: Decimal | None = Field(default=None, ge=0)
    observacoes: str | None = None


class NotaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    avaliacao_id: uuid.UUID
    aluno_id: uuid.UUID
    valor: Decimal
    observacoes: str | None
    lancado_por: uuid.UUID
    lancado_em: datetime
    created_at: datetime


# ── Falta ───────────────────────────────────────

class FaltaInput(BaseModel):
    aluno_id: uuid.UUID
    disciplina_id: uuid.UUID
    tipo: str = Field(pattern="^(justificada|injustificada)$")
    justificativa: str | None = None


class LancarFaltasRequest(BaseModel):
    turma_id: uuid.UUID
    data: date
    faltas: list[FaltaInput] = Field(min_length=1)


class FaltaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    aluno_id: uuid.UUID
    turma_id: uuid.UUID
    disciplina_id: uuid.UUID
    data: date
    tipo: str
    justificativa: str | None
    created_at: datetime


class FaltaResumoResponse(BaseModel):
    total: int
    justificadas: int
    injustificadas: int
    por_disciplina: list[dict]


# ── Boletim ─────────────────────────────────────

class BoletimDisciplinaItem(BaseModel):
    disciplina_id: uuid.UUID
    disciplina_nome: str
    media: Decimal | None
    faltas_total: int


class BoletimResponse(BaseModel):
    aluno_id: uuid.UUID
    ano_letivo_id: uuid.UUID
    periodo: int
    disciplinas: list[BoletimDisciplinaItem]
