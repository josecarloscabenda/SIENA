"""FastAPI router for the avaliacoes module."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.auth.middleware import CurrentUser, get_current_user
from src.common.auth.rbac import require_role
from src.common.database.session import get_db
from src.modules.avaliacoes.api.dtos import (
    AvaliacaoDetailResponse,
    AvaliacaoListResponse,
    AvaliacaoResponse,
    BoletimResponse,
    CreateAvaliacaoRequest,
    FaltaResumoResponse,
    FaltaResponse,
    LancarFaltasRequest,
    LancarNotasRequest,
    NotaResponse,
    UpdateNotaRequest,
)
from src.modules.avaliacoes.application.services import (
    AvaliacoesError,
    BoletimService,
    FaltaService,
    InvalidDataError,
    NotaService,
    NotFoundError,
)

router = APIRouter()


def _handle_error(e: AvaliacoesError) -> HTTPException:
    if isinstance(e, NotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    if isinstance(e, InvalidDataError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ── Avaliações ──────────────────────────────────

@router.post(
    "/avaliacoes",
    response_model=AvaliacaoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin", "diretor", "professor"))],
)
async def create_avaliacao(
    body: CreateAvaliacaoRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AvaliacaoResponse:
    svc = NotaService(db)
    avaliacao = await svc.create_avaliacao(
        tenant_id=current_user.tenant_id,
        turma_id=body.turma_id,
        disciplina_id=body.disciplina_id,
        tipo=body.tipo,
        periodo=body.periodo,
        data=body.data,
        peso=body.peso,
        nota_maxima=body.nota_maxima,
    )
    return AvaliacaoResponse.model_validate(avaliacao)


@router.get("/avaliacoes", response_model=AvaliacaoListResponse)
async def list_avaliacoes(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    turma_id: uuid.UUID | None = Query(default=None),
    disciplina_id: uuid.UUID | None = Query(default=None),
    periodo: int | None = Query(default=None),
) -> AvaliacaoListResponse:
    svc = NotaService(db)
    items, total = await svc.list_avaliacoes(
        current_user.tenant_id, offset, limit, turma_id, disciplina_id, periodo
    )
    return AvaliacaoListResponse(
        total=total, offset=offset, limit=limit,
        items=[AvaliacaoResponse.model_validate(a) for a in items],
    )


# ── Notas ───────────────────────────────────────

@router.post(
    "/avaliacoes/{avaliacao_id}/notas",
    response_model=list[NotaResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin", "diretor", "professor"))],
)
async def lancar_notas(
    avaliacao_id: uuid.UUID,
    body: LancarNotasRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[NotaResponse]:
    svc = NotaService(db)
    try:
        notas = await svc.lancar_notas(
            tenant_id=current_user.tenant_id,
            avaliacao_id=avaliacao_id,
            professor_id=current_user.user_id,
            notas=[n.model_dump() for n in body.notas],
        )
    except AvaliacoesError as e:
        raise _handle_error(e) from e
    return [NotaResponse.model_validate(n) for n in notas]


@router.get(
    "/avaliacoes/{avaliacao_id}/notas",
    response_model=list[NotaResponse],
)
async def list_notas_avaliacao(
    avaliacao_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[NotaResponse]:
    svc = NotaService(db)
    try:
        notas = await svc.list_notas_avaliacao(avaliacao_id, current_user.tenant_id)
    except AvaliacoesError as e:
        raise _handle_error(e) from e
    return [NotaResponse.model_validate(n) for n in notas]


@router.patch(
    "/notas/{nota_id}",
    response_model=NotaResponse,
    dependencies=[Depends(require_role("super_admin", "diretor", "professor"))],
)
async def update_nota(
    nota_id: uuid.UUID,
    body: UpdateNotaRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotaResponse:
    svc = NotaService(db)
    try:
        nota = await svc.update_nota(
            nota_id, current_user.tenant_id, body.valor, body.observacoes
        )
    except AvaliacoesError as e:
        raise _handle_error(e) from e
    return NotaResponse.model_validate(nota)


@router.get("/alunos/{aluno_id}/notas", response_model=list[NotaResponse])
async def list_notas_aluno(
    aluno_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    periodo: int | None = Query(default=None),
) -> list[NotaResponse]:
    svc = NotaService(db)
    notas = await svc.list_notas_aluno(aluno_id, current_user.tenant_id, periodo)
    return [NotaResponse.model_validate(n) for n in notas]


@router.get("/turmas/{turma_id}/notas", response_model=list[NotaResponse])
async def list_notas_turma(
    turma_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    periodo: int | None = Query(default=None),
) -> list[NotaResponse]:
    svc = NotaService(db)
    notas = await svc.list_notas_turma(turma_id, current_user.tenant_id, periodo)
    return [NotaResponse.model_validate(n) for n in notas]


# ── Faltas ──────────────────────────────────────

@router.post(
    "/faltas",
    response_model=list[FaltaResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin", "diretor", "professor"))],
)
async def lancar_faltas(
    body: LancarFaltasRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[FaltaResponse]:
    svc = FaltaService(db)
    faltas = await svc.lancar_faltas(
        tenant_id=current_user.tenant_id,
        turma_id=body.turma_id,
        data=body.data,
        faltas=[f.model_dump() for f in body.faltas],
    )
    return [FaltaResponse.model_validate(f) for f in faltas]


@router.get("/alunos/{aluno_id}/faltas", response_model=list[FaltaResponse])
async def list_faltas_aluno(
    aluno_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    disciplina_id: uuid.UUID | None = Query(default=None),
    tipo: str | None = Query(default=None),
) -> list[FaltaResponse]:
    svc = FaltaService(db)
    faltas = await svc.list_faltas_aluno(
        aluno_id, current_user.tenant_id, disciplina_id, tipo
    )
    return [FaltaResponse.model_validate(f) for f in faltas]


@router.get("/alunos/{aluno_id}/faltas/resumo", response_model=FaltaResumoResponse)
async def resumo_faltas(
    aluno_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FaltaResumoResponse:
    svc = FaltaService(db)
    resumo = await svc.resumo_faltas(aluno_id, current_user.tenant_id)
    return FaltaResumoResponse(**resumo)


# ── Boletim ─────────────────────────────────────

@router.get("/alunos/{aluno_id}/boletim", response_model=BoletimResponse)
async def get_boletim(
    aluno_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    periodo: int = Query(ge=1, le=3),
) -> BoletimResponse:
    svc = BoletimService(db)
    boletim = await svc.gerar_boletim(aluno_id, current_user.tenant_id, periodo)
    return BoletimResponse(**boletim)
