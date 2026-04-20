"""Pydantic DTOs for the enrollment module."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
# Matrícula
# ──────────────────────────────────────────────

class CreateMatriculaRequest(BaseModel):
    aluno_id: uuid.UUID
    ano_letivo_id: uuid.UUID
    classe: str = Field(min_length=1, max_length=10)
    turno: str = Field(
        default="matutino",
        pattern="^(matutino|vespertino|nocturno)$",
    )
    observacoes: str | None = None


class MatriculaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    aluno_id: uuid.UUID
    aluno_nome: str | None = None
    aluno_n_processo: str | None = None
    ano_letivo_id: uuid.UUID
    ano_letivo_designacao: str | None = None
    classe: str
    turno: str
    estado: str
    data_pedido: date
    data_aprovacao: date | None
    observacoes: str | None
    created_at: datetime


class MatriculaDetailResponse(MatriculaResponse):
    alocacao: "AlocacaoTurmaResponse | None" = None
    documentos: list["DocumentoMatriculaResponse"] = []


class MatriculaListResponse(BaseModel):
    total: int
    offset: int
    limit: int
    items: list[MatriculaResponse]


# ──────────────────────────────────────────────
# Aprovação / Rejeição
# ──────────────────────────────────────────────

class RejectMatriculaRequest(BaseModel):
    motivo: str = Field(min_length=1)


# ──────────────────────────────────────────────
# Alocação em Turma
# ──────────────────────────────────────────────

class CreateAlocacaoRequest(BaseModel):
    turma_id: uuid.UUID


class AlocacaoTurmaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    matricula_id: uuid.UUID
    turma_id: uuid.UUID
    data_alocacao: date
    created_at: datetime


# ──────────────────────────────────────────────
# Transferência
# ──────────────────────────────────────────────

class CreateTransferenciaRequest(BaseModel):
    aluno_id: uuid.UUID
    escola_destino_id: uuid.UUID
    motivo: str = Field(min_length=1)


class TransferenciaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    tenant_id: uuid.UUID
    aluno_id: uuid.UUID
    escola_origem_id: uuid.UUID
    escola_destino_id: uuid.UUID
    data_pedido: date
    estado: str
    motivo: str
    documentos_url: dict | None
    created_at: datetime


# ──────────────────────────────────────────────
# Documentos de Matrícula
# ──────────────────────────────────────────────

class CreateDocumentoRequest(BaseModel):
    tipo: str = Field(min_length=1, max_length=50)
    url: str = Field(min_length=1, max_length=500)


class DocumentoMatriculaResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    matricula_id: uuid.UUID
    tipo: str
    url: str
    verificado: bool
    uploaded_at: datetime
    created_at: datetime