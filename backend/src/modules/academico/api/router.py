"""FastAPI router for the academico module."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.auth.middleware import CurrentUser, get_current_user
from src.common.auth.rbac import require_role
from src.common.database.session import get_db
from src.modules.academico.api.dtos import (
    CreateCurriculoRequest,
    CreateDiarioRequest,
    CreateDisciplinaRequest,
    CreateHorarioRequest,
    CreateTurmaRequest,
    CurriculoDetailResponse,
    CurriculoListResponse,
    CurriculoResponse,
    DiarioClasseResponse,
    DiarioListResponse,
    DisciplinaListResponse,
    DisciplinaResponse,
    HorarioAulaResponse,
    TurmaDetailResponse,
    TurmaListResponse,
    TurmaResponse,
)
from src.modules.academico.application.services import (
    AcademicoError,
    ConflictError,
    CurriculoService,
    DiarioService,
    DisciplinaService,
    DuplicateCodigoError,
    HorarioService,
    InvalidDataError,
    NotFoundError,
    TurmaService,
)

router = APIRouter()


def _handle_error(e: AcademicoError) -> HTTPException:
    if isinstance(e, NotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    if isinstance(e, (ConflictError, DuplicateCodigoError)):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    if isinstance(e, InvalidDataError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ── Currículos ──────────────────────────────────

@router.post(
    "/curriculos",
    response_model=CurriculoDetailResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin", "diretor"))],
)
async def create_curriculo(
    body: CreateCurriculoRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CurriculoDetailResponse:
    svc = CurriculoService(db)
    curriculo = await svc.create_curriculo(
        tenant_id=current_user.tenant_id,
        nivel=body.nivel,
        classe=body.classe,
        ano_letivo_id=body.ano_letivo_id,
        carga_horaria_total=body.carga_horaria_total,
    )
    return CurriculoDetailResponse.model_validate(curriculo)


@router.get("/curriculos", response_model=CurriculoListResponse)
async def list_curriculos(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> CurriculoListResponse:
    svc = CurriculoService(db)
    items, total = await svc.list_curriculos(current_user.tenant_id, offset, limit)
    return CurriculoListResponse(
        total=total, offset=offset, limit=limit,
        items=[CurriculoResponse.model_validate(c) for c in items],
    )


# ── Disciplinas ─────────────────────────────────

@router.post(
    "/disciplinas",
    response_model=DisciplinaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin", "diretor"))],
)
async def create_disciplina(
    body: CreateDisciplinaRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DisciplinaResponse:
    svc = DisciplinaService(db)
    try:
        disciplina = await svc.create_disciplina(
            tenant_id=current_user.tenant_id,
            nome=body.nome,
            codigo=body.codigo,
            curriculo_id=body.curriculo_id,
            carga_horaria_semanal=body.carga_horaria_semanal,
        )
    except AcademicoError as e:
        raise _handle_error(e) from e
    return DisciplinaResponse.model_validate(disciplina)


@router.get("/disciplinas", response_model=DisciplinaListResponse)
async def list_disciplinas(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    curriculo_id: uuid.UUID | None = Query(default=None),
) -> DisciplinaListResponse:
    svc = DisciplinaService(db)
    items, total = await svc.list_disciplinas(
        current_user.tenant_id, offset, limit, curriculo_id
    )
    return DisciplinaListResponse(
        total=total, offset=offset, limit=limit,
        items=[DisciplinaResponse.model_validate(d) for d in items],
    )


# ── Turmas ──────────────────────────────────────

@router.post(
    "/turmas",
    response_model=TurmaDetailResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin", "diretor"))],
)
async def create_turma(
    body: CreateTurmaRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TurmaDetailResponse:
    svc = TurmaService(db)
    turma = await svc.create_turma(
        tenant_id=current_user.tenant_id,
        nome=body.nome,
        classe=body.classe,
        turno=body.turno,
        ano_letivo_id=body.ano_letivo_id,
        capacidade_max=body.capacidade_max,
        professor_regente_id=body.professor_regente_id,
        sala=body.sala,
    )
    return TurmaDetailResponse.model_validate(turma)


@router.get("/turmas", response_model=TurmaListResponse)
async def list_turmas(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    ano_letivo_id: uuid.UUID | None = Query(default=None),
    classe: str | None = Query(default=None),
    turno: str | None = Query(default=None),
) -> TurmaListResponse:
    svc = TurmaService(db)
    items, total = await svc.list_turmas(
        current_user.tenant_id, offset, limit, ano_letivo_id, classe, turno
    )
    return TurmaListResponse(
        total=total, offset=offset, limit=limit,
        items=[TurmaResponse.model_validate(t) for t in items],
    )


@router.get("/turmas/{turma_id}", response_model=TurmaDetailResponse)
async def get_turma(
    turma_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TurmaDetailResponse:
    svc = TurmaService(db)
    turma = await svc.get_turma(turma_id, current_user.tenant_id)
    if turma is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada")
    return TurmaDetailResponse.model_validate(turma)


# ── Horários ────────────────────────────────────

@router.post(
    "/turmas/{turma_id}/horarios",
    response_model=HorarioAulaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin", "diretor"))],
)
async def create_horario(
    turma_id: uuid.UUID,
    body: CreateHorarioRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HorarioAulaResponse:
    svc = HorarioService(db)
    try:
        horario = await svc.create_horario(
            tenant_id=current_user.tenant_id,
            turma_id=turma_id,
            disciplina_id=body.disciplina_id,
            professor_id=body.professor_id,
            dia_semana=body.dia_semana,
            hora_inicio=body.hora_inicio,
            hora_fim=body.hora_fim,
        )
    except AcademicoError as e:
        raise _handle_error(e) from e
    return HorarioAulaResponse.model_validate(horario)


@router.get("/turmas/{turma_id}/horarios", response_model=list[HorarioAulaResponse])
async def list_horarios_turma(
    turma_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[HorarioAulaResponse]:
    svc = HorarioService(db)
    try:
        horarios = await svc.list_horarios_turma(turma_id, current_user.tenant_id)
    except AcademicoError as e:
        raise _handle_error(e) from e
    return [HorarioAulaResponse.model_validate(h) for h in horarios]


@router.get(
    "/professores/{professor_id}/horarios",
    response_model=list[HorarioAulaResponse],
)
async def list_horarios_professor(
    professor_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[HorarioAulaResponse]:
    svc = HorarioService(db)
    horarios = await svc.list_horarios_professor(professor_id, current_user.tenant_id)
    return [HorarioAulaResponse.model_validate(h) for h in horarios]


# ── Diário de Classe ────────────────────────────

@router.post(
    "/diario",
    response_model=DiarioClasseResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin", "diretor", "professor"))],
)
async def registar_aula(
    body: CreateDiarioRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DiarioClasseResponse:
    svc = DiarioService(db)
    presencas = [p.model_dump() for p in body.presencas] if body.presencas else None
    try:
        diario = await svc.registar_aula(
            tenant_id=current_user.tenant_id,
            professor_id=current_user.user_id,
            turma_id=body.turma_id,
            disciplina_id=body.disciplina_id,
            data_aula=body.data_aula,
            conteudo=body.conteudo,
            sumario=body.sumario,
            observacoes=body.observacoes,
            presencas=presencas,
        )
    except AcademicoError as e:
        raise _handle_error(e) from e
    return DiarioClasseResponse.model_validate(diario)


@router.get("/turmas/{turma_id}/diario", response_model=DiarioListResponse)
async def list_diarios(
    turma_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    disciplina_id: uuid.UUID | None = Query(default=None),
) -> DiarioListResponse:
    svc = DiarioService(db)
    items, total = await svc.list_diarios(
        current_user.tenant_id, turma_id, offset, limit, disciplina_id
    )
    return DiarioListResponse(
        total=total, offset=offset, limit=limit,
        items=[DiarioClasseResponse.model_validate(d) for d in items],
    )
