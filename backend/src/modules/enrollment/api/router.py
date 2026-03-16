"""FastAPI router for the enrollment module."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.auth.middleware import CurrentUser, get_current_user
from src.common.auth.rbac import require_role
from src.common.database.session import get_db
from src.modules.enrollment.api.dtos import (
    AlocacaoTurmaResponse,
    CreateAlocacaoRequest,
    CreateDocumentoRequest,
    CreateMatriculaRequest,
    CreateTransferenciaRequest,
    DocumentoMatriculaResponse,
    MatriculaDetailResponse,
    MatriculaListResponse,
    MatriculaResponse,
    RejectMatriculaRequest,
    TransferenciaResponse,
)
from src.modules.enrollment.application.services import (
    AlocacaoService,
    DocumentoService,
    DuplicateAlocacaoError,
    DuplicateMatriculaError,
    EnrollmentError,
    InvalidStateError,
    MatriculaService,
    NotFoundError,
    TransferenciaService,
)

router = APIRouter()


def _handle_enrollment_error(e: EnrollmentError) -> HTTPException:
    if isinstance(e, NotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    if isinstance(e, (DuplicateMatriculaError, DuplicateAlocacaoError)):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    if isinstance(e, InvalidStateError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ──────────────────────────────────────────────
# Matrículas
# ──────────────────────────────────────────────

@router.post(
    "/matriculas",
    response_model=MatriculaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin", "diretor", "secretaria"))],
)
async def create_matricula(
    body: CreateMatriculaRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MatriculaResponse:
    """Cria novo pedido de matrícula."""
    svc = MatriculaService(db)
    try:
        matricula = await svc.create_matricula(
            tenant_id=current_user.tenant_id,
            aluno_id=body.aluno_id,
            ano_letivo_id=body.ano_letivo_id,
            classe=body.classe,
            turno=body.turno,
            observacoes=body.observacoes,
        )
    except EnrollmentError as e:
        raise _handle_enrollment_error(e) from e
    return MatriculaResponse.model_validate(matricula)


@router.get("/matriculas", response_model=MatriculaListResponse)
async def list_matriculas(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    ano_letivo_id: uuid.UUID | None = Query(default=None),
    classe: str | None = Query(default=None),
    estado: str | None = Query(default=None),
    turno: str | None = Query(default=None),
) -> MatriculaListResponse:
    """Lista matrículas com filtros e paginação."""
    svc = MatriculaService(db)
    matriculas, total = await svc.list_matriculas(
        tenant_id=current_user.tenant_id,
        offset=offset,
        limit=limit,
        ano_letivo_id=ano_letivo_id,
        classe=classe,
        estado=estado,
        turno=turno,
    )
    return MatriculaListResponse(
        total=total,
        offset=offset,
        limit=limit,
        items=[MatriculaResponse.model_validate(m) for m in matriculas],
    )


@router.patch(
    "/matriculas/{matricula_id}/aprovar",
    response_model=MatriculaResponse,
    dependencies=[Depends(require_role("super_admin", "diretor"))],
)
async def aprovar_matricula(
    matricula_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MatriculaResponse:
    """Aprova uma matrícula pendente."""
    svc = MatriculaService(db)
    try:
        matricula = await svc.aprovar_matricula(matricula_id, current_user.tenant_id)
    except EnrollmentError as e:
        raise _handle_enrollment_error(e) from e
    return MatriculaResponse.model_validate(matricula)


@router.patch(
    "/matriculas/{matricula_id}/rejeitar",
    response_model=MatriculaResponse,
    dependencies=[Depends(require_role("super_admin", "diretor"))],
)
async def rejeitar_matricula(
    matricula_id: uuid.UUID,
    body: RejectMatriculaRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MatriculaResponse:
    """Rejeita uma matrícula pendente com motivo."""
    svc = MatriculaService(db)
    try:
        matricula = await svc.rejeitar_matricula(
            matricula_id, current_user.tenant_id, body.motivo
        )
    except EnrollmentError as e:
        raise _handle_enrollment_error(e) from e
    return MatriculaResponse.model_validate(matricula)


# ──────────────────────────────────────────────
# Alocação em Turma
# ──────────────────────────────────────────────

@router.post(
    "/matriculas/{matricula_id}/alocacao",
    response_model=AlocacaoTurmaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin", "diretor", "secretaria"))],
)
async def alocar_em_turma(
    matricula_id: uuid.UUID,
    body: CreateAlocacaoRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AlocacaoTurmaResponse:
    """Aloca aluno matriculado numa turma."""
    svc = AlocacaoService(db)
    try:
        alocacao = await svc.alocar_em_turma(
            tenant_id=current_user.tenant_id,
            matricula_id=matricula_id,
            turma_id=body.turma_id,
        )
    except EnrollmentError as e:
        raise _handle_enrollment_error(e) from e
    return AlocacaoTurmaResponse.model_validate(alocacao)


# ──────────────────────────────────────────────
# Transferências
# ──────────────────────────────────────────────

@router.post(
    "/transferencias",
    response_model=TransferenciaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin", "diretor", "secretaria"))],
)
async def create_transferencia(
    body: CreateTransferenciaRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TransferenciaResponse:
    """Cria pedido de transferência."""
    svc = TransferenciaService(db)
    try:
        transferencia = await svc.create_transferencia(
            tenant_id=current_user.tenant_id,
            aluno_id=body.aluno_id,
            escola_origem_id=uuid.uuid4(),  # TODO: get from current escola context
            escola_destino_id=body.escola_destino_id,
            motivo=body.motivo,
        )
    except EnrollmentError as e:
        raise _handle_enrollment_error(e) from e
    return TransferenciaResponse.model_validate(transferencia)


@router.patch(
    "/transferencias/{transferencia_id}/aprovar",
    response_model=TransferenciaResponse,
    dependencies=[Depends(require_role("super_admin", "diretor"))],
)
async def aprovar_transferencia(
    transferencia_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TransferenciaResponse:
    """Aprova pedido de transferência."""
    svc = TransferenciaService(db)
    try:
        transferencia = await svc.aprovar_transferencia(
            transferencia_id, current_user.tenant_id
        )
    except EnrollmentError as e:
        raise _handle_enrollment_error(e) from e
    return TransferenciaResponse.model_validate(transferencia)


# ──────────────────────────────────────────────
# Documentos de Matrícula
# ──────────────────────────────────────────────

@router.get(
    "/matriculas/{matricula_id}/documentos",
    response_model=list[DocumentoMatriculaResponse],
)
async def list_documentos(
    matricula_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[DocumentoMatriculaResponse]:
    """Lista documentos de uma matrícula."""
    svc = DocumentoService(db)
    try:
        docs = await svc.list_documentos(matricula_id, current_user.tenant_id)
    except EnrollmentError as e:
        raise _handle_enrollment_error(e) from e
    return [DocumentoMatriculaResponse.model_validate(d) for d in docs]


@router.post(
    "/matriculas/{matricula_id}/documentos",
    response_model=DocumentoMatriculaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin", "diretor", "secretaria"))],
)
async def upload_documento(
    matricula_id: uuid.UUID,
    body: CreateDocumentoRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentoMatriculaResponse:
    """Adiciona documento a uma matrícula."""
    svc = DocumentoService(db)
    try:
        doc = await svc.add_documento(
            tenant_id=current_user.tenant_id,
            matricula_id=matricula_id,
            tipo=body.tipo,
            url=body.url,
        )
    except EnrollmentError as e:
        raise _handle_enrollment_error(e) from e
    return DocumentoMatriculaResponse.model_validate(doc)
