"""FastAPI router for the escolas module."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.auth.middleware import CurrentUser, get_current_user
from src.common.auth.rbac import require_role
from src.common.database.session import get_db
from src.modules.escolas.api.dtos import (
    AnoLetivoResponse,
    CreateAnoLetivoRequest,
    CreateEscolaRequest,
    EscolaDetailResponse,
    EscolaListResponse,
    EscolaResponse,
    InfraestruturaResponse,
    UpdateEscolaRequest,
)
from src.modules.escolas.application.services import EscolaService

router = APIRouter()


@router.post(
    "/escolas",
    response_model=EscolaDetailResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin", "diretor"))],
)
async def create_escola(
    body: CreateEscolaRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EscolaDetailResponse:
    """Create a new escola for the current tenant."""
    svc = EscolaService(db)
    try:
        escola = await svc.create_escola(
            tenant_id=current_user.tenant_id,
            nome=body.nome,
            provincia=body.provincia,
            municipio=body.municipio,
            tipo=body.tipo,
            nivel_ensino=body.nivel_ensino,
            codigo_sige=body.codigo_sige,
            comuna=body.comuna,
            endereco=body.endereco,
            telefone=body.telefone,
            email=body.email,
            latitude=body.latitude,
            longitude=body.longitude,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return EscolaDetailResponse.model_validate(escola)


@router.get("/escolas", response_model=EscolaListResponse)
async def list_escolas(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    provincia: str | None = Query(default=None),
    municipio: str | None = Query(default=None),
) -> EscolaListResponse:
    """List escolas for the current tenant, with optional filters."""
    svc = EscolaService(db)
    escolas, total = await svc.list_escolas(
        tenant_id=current_user.tenant_id,
        offset=offset,
        limit=limit,
        provincia=provincia,
        municipio=municipio,
    )
    return EscolaListResponse(
        total=total,
        offset=offset,
        limit=limit,
        items=[EscolaResponse.model_validate(e) for e in escolas],
    )


@router.get("/escolas/{escola_id}", response_model=EscolaDetailResponse)
async def get_escola(
    escola_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EscolaDetailResponse:
    """Get escola detail with anos letivos, infraestruturas and configuracao."""
    svc = EscolaService(db)
    escola = await svc.get_escola(escola_id, current_user.tenant_id)
    if escola is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escola não encontrada")
    return EscolaDetailResponse.model_validate(escola)


@router.patch(
    "/escolas/{escola_id}",
    response_model=EscolaDetailResponse,
    dependencies=[Depends(require_role("super_admin", "diretor"))],
)
async def update_escola(
    escola_id: uuid.UUID,
    body: UpdateEscolaRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EscolaDetailResponse:
    """Update escola fields."""
    svc = EscolaService(db)
    fields = body.model_dump(exclude_unset=True)
    try:
        escola = await svc.update_escola(escola_id, current_user.tenant_id, **fields)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return EscolaDetailResponse.model_validate(escola)


@router.post(
    "/escolas/{escola_id}/ano-letivo",
    response_model=AnoLetivoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin", "diretor"))],
)
async def abrir_ano_letivo(
    escola_id: uuid.UUID,
    body: CreateAnoLetivoRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnoLetivoResponse:
    """Open a new ano letivo for an escola. Deactivates any previous active one."""
    svc = EscolaService(db)
    try:
        ano = await svc.abrir_ano_letivo(
            escola_id=escola_id,
            tenant_id=current_user.tenant_id,
            ano=body.ano,
            designacao=body.designacao,
            data_inicio=body.data_inicio,
            data_fim=body.data_fim,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return AnoLetivoResponse.model_validate(ano)


@router.get("/escolas/{escola_id}/infraestruturas", response_model=list[InfraestruturaResponse])
async def list_infraestruturas(
    escola_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[InfraestruturaResponse]:
    """List infraestruturas of an escola."""
    svc = EscolaService(db)
    try:
        infras = await svc.list_infraestruturas(escola_id, current_user.tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return [InfraestruturaResponse.model_validate(i) for i in infras]