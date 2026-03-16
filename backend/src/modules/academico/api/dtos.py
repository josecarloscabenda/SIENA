"""Pydantic DTOs for the academico module."""

import uuid
from datetime import date, datetime, time

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
# Currículo
# ──────────────────────────────────────────────

class CreateCurriculoRequest(BaseModel):
    nivel: str = Field(
        min_length=1,
        pattern="^(primario|secundario_1ciclo|secundario_2ciclo|tecnico)$",
    )
    classe: str = Field(min_length=1, max_length=10)
    ano_letivo_id: uuid.UUID
    carga_horaria_total: int = Field(ge=1, le=60)


class CurriculoResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    nivel: str
    classe: str
    ano_letivo_id: uuid.UUID
    carga_horaria_total: int
    created_at: datetime


class CurriculoDetailResponse(CurriculoResponse):
    disciplinas: list["DisciplinaResponse"] = []


class CurriculoListResponse(BaseModel):
    total: int
    offset: int
    limit: int
    items: list[CurriculoResponse]


# ──────────────────────────────────────────────
# Disciplina
# ──────────────────────────────────────────────

class CreateDisciplinaRequest(BaseModel):
    nome: str = Field(min_length=1, max_length=255)
    codigo: str = Field(min_length=1, max_length=50)
    curriculo_id: uuid.UUID
    carga_horaria_semanal: int = Field(ge=1, le=20)


class DisciplinaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    nome: str
    codigo: str
    curriculo_id: uuid.UUID
    carga_horaria_semanal: int
    created_at: datetime


class DisciplinaListResponse(BaseModel):
    total: int
    offset: int
    limit: int
    items: list[DisciplinaResponse]


# ──────────────────────────────────────────────
# Turma
# ──────────────────────────────────────────────

class CreateTurmaRequest(BaseModel):
    nome: str = Field(min_length=1, max_length=50)
    classe: str = Field(min_length=1, max_length=10)
    turno: str = Field(pattern="^(matutino|vespertino|nocturno)$")
    ano_letivo_id: uuid.UUID
    capacidade_max: int = Field(ge=1, le=100)
    professor_regente_id: uuid.UUID
    sala: str | None = Field(default=None, max_length=100)


class TurmaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    nome: str
    classe: str
    turno: str
    ano_letivo_id: uuid.UUID
    capacidade_max: int
    professor_regente_id: uuid.UUID
    sala: str | None
    created_at: datetime


class TurmaDetailResponse(TurmaResponse):
    horarios: list["HorarioAulaResponse"] = []


class TurmaListResponse(BaseModel):
    total: int
    offset: int
    limit: int
    items: list[TurmaResponse]


# ──────────────────────────────────────────────
# Horário de Aula
# ──────────────────────────────────────────────

class CreateHorarioRequest(BaseModel):
    disciplina_id: uuid.UUID
    professor_id: uuid.UUID
    dia_semana: str = Field(
        pattern="^(segunda|terca|quarta|quinta|sexta|sabado)$"
    )
    hora_inicio: time
    hora_fim: time


class HorarioAulaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    turma_id: uuid.UUID
    disciplina_id: uuid.UUID
    professor_id: uuid.UUID
    dia_semana: str
    hora_inicio: time
    hora_fim: time
    created_at: datetime


# ──────────────────────────────────────────────
# Diário de Classe
# ──────────────────────────────────────────────

class PresencaInput(BaseModel):
    aluno_id: uuid.UUID
    presente: bool
    justificativa: str | None = None


class CreateDiarioRequest(BaseModel):
    turma_id: uuid.UUID
    disciplina_id: uuid.UUID
    data_aula: date
    conteudo: str = Field(min_length=1)
    sumario: str = Field(min_length=1)
    observacoes: str | None = None
    presencas: list[PresencaInput] = []


class PresencaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    diario_id: uuid.UUID
    aluno_id: uuid.UUID
    presente: bool
    justificativa: str | None


class DiarioClasseResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    turma_id: uuid.UUID
    disciplina_id: uuid.UUID
    professor_id: uuid.UUID
    data_aula: date
    conteudo: str
    sumario: str
    observacoes: str | None
    created_at: datetime
    presencas: list[PresencaResponse] = []


class DiarioListResponse(BaseModel):
    total: int
    offset: int
    limit: int
    items: list[DiarioClasseResponse]
