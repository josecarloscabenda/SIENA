"""FastAPI router for the directory module."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.auth.middleware import CurrentUser, get_current_user
from src.common.auth.rbac import require_role
from src.common.database.session import get_db
from src.modules.directory.api.dtos import (
    AlunoDetailResponse,
    AlunoListResponse,
    AlunoResponse,
    CreateAlunoRequest,
    CreateEncarregadoRequest,
    CreateProfessorRequest,
    CreateVinculoRequest,
    EncarregadoListResponse,
    EncarregadoResponse,
    ProfessorListResponse,
    ProfessorResponse,
    UpdateAlunoRequest,
    UpdateProfessorRequest,
    VinculoResponse,
)
from src.modules.directory.application.services import (
    DirectoryError,
    DuplicateBIError,
    DuplicateNProcessoError,
    DuplicateVinculoError,
    NotFoundError,
    PessoaService,
    VinculoService,
)

router = APIRouter()


def _handle_directory_error(e: DirectoryError) -> HTTPException:
    """Map domain errors to HTTP status codes."""
    if isinstance(e, NotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    if isinstance(e, (DuplicateBIError, DuplicateNProcessoError, DuplicateVinculoError)):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ──────────────────────────────────────────────
# Alunos
# ──────────────────────────────────────────────

@router.post(
    "/alunos",
    response_model=AlunoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin", "diretor", "secretaria"))],
)
async def create_aluno(
    body: CreateAlunoRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AlunoResponse:
    """Regista um novo aluno (pessoa + aluno)."""
    svc = PessoaService(db)
    try:
        aluno = await svc.create_aluno(
            tenant_id=current_user.tenant_id,
            nome_completo=body.nome_completo,
            bi_identificacao=body.bi_identificacao,
            dt_nascimento=body.dt_nascimento,
            sexo=body.sexo,
            nacionalidade=body.nacionalidade,
            morada=body.morada,
            telefone=body.telefone,
            email=body.email,
            foto_url=body.foto_url,
            n_processo=body.n_processo,
            ano_ingresso=body.ano_ingresso,
            necessidades_especiais=body.necessidades_especiais,
            status=body.status,
        )
    except DirectoryError as e:
        raise _handle_directory_error(e) from e
    return AlunoResponse.model_validate(aluno)


@router.get("/alunos", response_model=AlunoListResponse)
async def list_alunos(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    nome: str | None = Query(default=None),
    n_processo: str | None = Query(default=None),
    status: str | None = Query(default=None),
) -> AlunoListResponse:
    """Lista alunos do tenant com paginação e filtros."""
    svc = PessoaService(db)
    alunos, total = await svc.list_alunos(
        tenant_id=current_user.tenant_id,
        offset=offset,
        limit=limit,
        nome=nome,
        n_processo=n_processo,
        status=status,
    )
    return AlunoListResponse(
        total=total,
        offset=offset,
        limit=limit,
        items=[AlunoResponse.model_validate(a) for a in alunos],
    )


@router.get("/alunos/{aluno_id}", response_model=AlunoDetailResponse)
async def get_aluno(
    aluno_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AlunoDetailResponse:
    """Detalhe do aluno com vínculos a encarregados."""
    svc = PessoaService(db)
    aluno = await svc.get_aluno_detail(aluno_id, current_user.tenant_id)
    if aluno is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado"
        )
    return AlunoDetailResponse.model_validate(aluno)


@router.patch(
    "/alunos/{aluno_id}",
    response_model=AlunoResponse,
    dependencies=[Depends(require_role("super_admin", "diretor", "secretaria"))],
)
async def update_aluno(
    aluno_id: uuid.UUID,
    body: UpdateAlunoRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AlunoResponse:
    """Edita dados do aluno e/ou da pessoa."""
    svc = PessoaService(db)
    fields = body.model_dump(exclude_unset=True)
    try:
        aluno = await svc.update_aluno(aluno_id, current_user.tenant_id, **fields)
    except DirectoryError as e:
        raise _handle_directory_error(e) from e
    return AlunoResponse.model_validate(aluno)


# ──────────────────────────────────────────────
# Professores
# ──────────────────────────────────────────────

@router.post(
    "/professores",
    response_model=ProfessorResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin", "diretor"))],
)
async def create_professor(
    body: CreateProfessorRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProfessorResponse:
    """Regista um novo professor (pessoa + professor)."""
    svc = PessoaService(db)
    try:
        professor = await svc.create_professor(
            tenant_id=current_user.tenant_id,
            nome_completo=body.nome_completo,
            bi_identificacao=body.bi_identificacao,
            dt_nascimento=body.dt_nascimento,
            sexo=body.sexo,
            nacionalidade=body.nacionalidade,
            morada=body.morada,
            telefone=body.telefone,
            email=body.email,
            foto_url=body.foto_url,
            codigo_funcional=body.codigo_funcional,
            especialidade=body.especialidade,
            carga_horaria_semanal=body.carga_horaria_semanal,
            tipo_contrato=body.tipo_contrato,
            nivel_academico=body.nivel_academico,
        )
    except DirectoryError as e:
        raise _handle_directory_error(e) from e
    return ProfessorResponse.model_validate(professor)


@router.get("/professores", response_model=ProfessorListResponse)
async def list_professores(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    especialidade: str | None = Query(default=None),
    tipo_contrato: str | None = Query(default=None),
) -> ProfessorListResponse:
    """Lista professores do tenant com paginação e filtros."""
    svc = PessoaService(db)
    professores, total = await svc.list_professores(
        tenant_id=current_user.tenant_id,
        offset=offset,
        limit=limit,
        especialidade=especialidade,
        tipo_contrato=tipo_contrato,
    )
    return ProfessorListResponse(
        total=total,
        offset=offset,
        limit=limit,
        items=[ProfessorResponse.model_validate(p) for p in professores],
    )


@router.get("/professores/{professor_id}", response_model=ProfessorResponse)
async def get_professor(
    professor_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProfessorResponse:
    """Detalhe do professor."""
    svc = PessoaService(db)
    professor = await svc.get_professor(professor_id, current_user.tenant_id)
    if professor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Professor não encontrado"
        )
    return ProfessorResponse.model_validate(professor)


@router.patch(
    "/professores/{professor_id}",
    response_model=ProfessorResponse,
    dependencies=[Depends(require_role("super_admin", "diretor"))],
)
async def update_professor(
    professor_id: uuid.UUID,
    body: UpdateProfessorRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProfessorResponse:
    """Edita dados do professor e/ou da pessoa."""
    svc = PessoaService(db)
    fields = body.model_dump(exclude_unset=True)
    try:
        professor = await svc.update_professor(
            professor_id, current_user.tenant_id, **fields
        )
    except DirectoryError as e:
        raise _handle_directory_error(e) from e
    return ProfessorResponse.model_validate(professor)


# ──────────────────────────────────────────────
# Encarregados
# ──────────────────────────────────────────────

@router.post(
    "/encarregados",
    response_model=EncarregadoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin", "diretor", "secretaria"))],
)
async def create_encarregado(
    body: CreateEncarregadoRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EncarregadoResponse:
    """Regista um novo encarregado de educação (pessoa + encarregado)."""
    svc = PessoaService(db)
    try:
        encarregado = await svc.create_encarregado(
            tenant_id=current_user.tenant_id,
            nome_completo=body.nome_completo,
            bi_identificacao=body.bi_identificacao,
            dt_nascimento=body.dt_nascimento,
            sexo=body.sexo,
            nacionalidade=body.nacionalidade,
            morada=body.morada,
            telefone=body.telefone,
            email=body.email,
            foto_url=body.foto_url,
            profissao=body.profissao,
            escolaridade=body.escolaridade,
        )
    except DirectoryError as e:
        raise _handle_directory_error(e) from e
    return EncarregadoResponse.model_validate(encarregado)


@router.get("/encarregados", response_model=EncarregadoListResponse)
async def list_encarregados(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> EncarregadoListResponse:
    """Lista encarregados do tenant com paginação."""
    svc = PessoaService(db)
    encarregados, total = await svc.list_encarregados(
        tenant_id=current_user.tenant_id,
        offset=offset,
        limit=limit,
    )
    return EncarregadoListResponse(
        total=total,
        offset=offset,
        limit=limit,
        items=[EncarregadoResponse.model_validate(e) for e in encarregados],
    )


# ──────────────────────────────────────────────
# Vínculos Aluno ↔ Encarregado
# ──────────────────────────────────────────────

@router.post(
    "/alunos/{aluno_id}/vinculos",
    response_model=VinculoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin", "diretor", "secretaria"))],
)
async def create_vinculo(
    aluno_id: uuid.UUID,
    body: CreateVinculoRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VinculoResponse:
    """Associa um encarregado a um aluno."""
    svc = VinculoService(db)
    try:
        vinculo = await svc.create_vinculo(
            tenant_id=current_user.tenant_id,
            aluno_id=aluno_id,
            encarregado_id=body.encarregado_id,
            tipo=body.tipo,
            principal=body.principal,
        )
    except DirectoryError as e:
        raise _handle_directory_error(e) from e
    return VinculoResponse.model_validate(vinculo)


@router.get("/alunos/{aluno_id}/vinculos", response_model=list[VinculoResponse])
async def list_vinculos(
    aluno_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[VinculoResponse]:
    """Lista vínculos (encarregados) de um aluno."""
    svc = VinculoService(db)
    try:
        vinculos = await svc.list_vinculos(aluno_id, current_user.tenant_id)
    except DirectoryError as e:
        raise _handle_directory_error(e) from e
    return [VinculoResponse.model_validate(v) for v in vinculos]