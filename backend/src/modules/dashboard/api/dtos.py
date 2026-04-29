"""DTOs for cross-module dashboard endpoints."""

import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class GestaoStats(BaseModel):
    total_alunos: int
    total_alunos_ativos: int
    total_professores: int
    total_encarregados: int
    total_turmas: int
    total_disciplinas: int
    matriculas_pendentes: int
    matriculas_aprovadas: int
    matriculas_rejeitadas: int
    avaliacoes_total: int
    notas_lancadas: int
    faltas_periodo_atual: int


class ProximaAulaItem(BaseModel):
    horario_id: uuid.UUID
    turma_id: uuid.UUID
    turma_nome: str
    disciplina_id: uuid.UUID
    disciplina_nome: str
    dia_semana: str
    hora_inicio: str
    hora_fim: str


class TurmaResumoProfessor(BaseModel):
    turma_id: uuid.UUID
    nome: str
    classe: str
    turno: str
    is_regente: bool
    leciona_disciplinas: int
    total_alunos: int


class ProfessorStats(BaseModel):
    professor_id: uuid.UUID
    nome: str
    turmas_atribuidas: int
    disciplinas_lecciona: int
    total_alunos: int
    notas_por_lancar: int        # avaliações sem nenhuma nota lançada
    proximas_aulas: list[ProximaAulaItem]
    turmas: list[TurmaResumoProfessor]


class AlunoDisciplinaResumo(BaseModel):
    disciplina_id: uuid.UUID
    disciplina_nome: str
    media: Decimal | None
    faltas: int


class ProximaAvaliacaoItem(BaseModel):
    avaliacao_id: uuid.UUID
    disciplina_id: uuid.UUID
    disciplina_nome: str
    tipo: str
    data: date
    nota_maxima: int


class AlunoStats(BaseModel):
    aluno_id: uuid.UUID
    nome: str
    n_processo: str
    matricula_id: uuid.UUID | None
    classe: str | None
    turma_id: uuid.UUID | None
    turma_nome: str | None
    media_geral: Decimal | None
    total_faltas: int
    faltas_justificadas: int
    faltas_injustificadas: int
    proximas_avaliacoes: list[ProximaAvaliacaoItem]
    disciplinas: list[AlunoDisciplinaResumo]


class EducandoResumo(BaseModel):
    aluno_id: uuid.UUID
    nome: str
    n_processo: str
    classe: str | None
    turma_nome: str | None
    media_geral: Decimal | None
    total_faltas: int
    faltas_injustificadas: int


class EncarregadoStats(BaseModel):
    encarregado_id: uuid.UUID
    nome: str
    educandos: list[EducandoResumo]


# ── Pauta ──────────────────────────────────────


class PautaAlunoLinha(BaseModel):
    aluno_id: uuid.UUID
    matricula_id: uuid.UUID
    nome: str
    n_processo: str
    medias_por_disciplina: dict[str, Decimal | None]   # key = disciplina_id (str)
    media_geral: Decimal | None


class PautaResponse(BaseModel):
    turma_id: uuid.UUID
    turma_nome: str
    classe: str
    ano_letivo_designacao: str | None
    periodo: int
    disciplinas: list[dict]  # [{id, nome, codigo}]
    linhas: list[PautaAlunoLinha]
