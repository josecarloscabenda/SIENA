"""FastAPI router for the escolas module."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.auth.middleware import CurrentUser, get_current_user
from src.common.auth.rbac import require_role
from src.common.database.session import get_db
from src.modules.escolas.api.dtos import (
    AnoLetivoLookupItem,
    AnoLetivoResponse,
    CreateAnoLetivoRequest,
    CreateEscolaRequest,
    CreateEscolaWithTenantRequest,
    CreateEscolaWithTenantResponse,
    CreateInfraestruturaRequest,
    DiretorResponse,
    EscolaDetailResponse,
    EscolaListResponse,
    EscolaLookupItem,
    EscolaResponse,
    InfraestruturaResponse,
    PessoaSimpleResponse,
    UpdateEscolaRequest,
    UpdateInfraestruturaRequest,
)
from src.modules.escolas.application.services import EscolaService
from src.modules.escolas.infrastructure.models import AnoLetivo, Escola

router = APIRouter()


@router.post(
    "/escolas/with-tenant",
    response_model=CreateEscolaWithTenantResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin"))],
)
async def create_escola_with_tenant(
    body: CreateEscolaWithTenantRequest,
    db: AsyncSession = Depends(get_db),
) -> CreateEscolaWithTenantResponse:
    """Super admin: create Tenant + Escola + Pessoa + Utilizador(diretor) in one operation."""
    svc = EscolaService(db)
    p = body.diretor_pessoa
    u = body.diretor_user
    try:
        result = await svc.create_escola_with_tenant(
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
            # Pessoa
            diretor_nome_completo=p.nome_completo,
            diretor_bi=p.bi_identificacao,
            diretor_dt_nascimento=p.dt_nascimento,
            diretor_sexo=p.sexo,
            diretor_nacionalidade=p.nacionalidade,
            diretor_morada=p.morada,
            diretor_telefone=p.telefone,
            diretor_email=p.email,
            # User
            diretor_username=u.username,
            diretor_password=u.password,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return CreateEscolaWithTenantResponse(
        tenant_id=result["tenant"].id,
        escola=EscolaResponse.model_validate(result["escola"]),
        diretor=DiretorResponse.model_validate(result["diretor"]),
        pessoa=PessoaSimpleResponse.model_validate(result["pessoa"]),
    )


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


# ──────────────────────────────────────────────
# Lookup endpoints (dropdowns)
# ──────────────────────────────────────────────

@router.get("/anos-letivos/lookup", response_model=list[AnoLetivoLookupItem])
async def lookup_anos_letivos(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    escola_id: uuid.UUID | None = Query(default=None),
    apenas_ativos: bool = Query(default=False),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[AnoLetivoLookupItem]:
    """Lista simplificada de anos letivos para dropdowns."""
    stmt = select(
        AnoLetivo.id,
        AnoLetivo.designacao,
        AnoLetivo.ano,
        AnoLetivo.ativo,
        AnoLetivo.escola_id,
    ).where(
        AnoLetivo.tenant_id == current_user.tenant_id,
        AnoLetivo.deleted_at.is_(None),
    )
    if escola_id:
        stmt = stmt.where(AnoLetivo.escola_id == escola_id)
    if apenas_ativos:
        stmt = stmt.where(AnoLetivo.ativo.is_(True))
    stmt = stmt.order_by(AnoLetivo.ano.desc()).limit(limit)
    result = await db.execute(stmt)
    return [
        AnoLetivoLookupItem(
            id=r.id,
            designacao=r.designacao,
            ano=r.ano,
            ativo=r.ativo,
            escola_id=r.escola_id,
        )
        for r in result.all()
    ]


@router.get("/escolas/lookup", response_model=list[EscolaLookupItem])
async def lookup_escolas(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[EscolaLookupItem]:
    """Lista simplificada de escolas do tenant para dropdowns."""
    stmt = (
        select(Escola.id, Escola.nome, Escola.provincia, Escola.municipio)
        .where(
            Escola.tenant_id == current_user.tenant_id,
            Escola.deleted_at.is_(None),
            Escola.ativa.is_(True),
        )
        .order_by(Escola.nome)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return [
        EscolaLookupItem(
            id=r.id, nome=r.nome, provincia=r.provincia, municipio=r.municipio
        )
        for r in result.all()
    ]


@router.get(
    "/escolas/all",
    response_model=EscolaListResponse,
    dependencies=[Depends(require_role("super_admin"))],
)
async def list_all_escolas(
    db: AsyncSession = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    provincia: str | None = Query(default=None),
) -> EscolaListResponse:
    """Super admin: list ALL escolas across all tenants."""
    svc = EscolaService(db)
    escolas, total = await svc.list_all_escolas(
        offset=offset,
        limit=limit,
        provincia=provincia,
    )
    return EscolaListResponse(
        total=total,
        offset=offset,
        limit=limit,
        items=[EscolaResponse.model_validate(e) for e in escolas],
    )


@router.get(
    "/escolas/all/{escola_id}",
    response_model=EscolaDetailResponse,
    dependencies=[Depends(require_role("super_admin"))],
)
async def get_escola_global(
    escola_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> EscolaDetailResponse:
    """Super admin: get escola detail without tenant filter."""
    svc = EscolaService(db)
    escola = await svc.get_escola_global(escola_id)
    if escola is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escola não encontrada")
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


@router.post(
    "/escolas/{escola_id}/infraestruturas",
    response_model=InfraestruturaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin", "diretor", "secretaria"))],
)
async def create_infraestrutura(
    escola_id: uuid.UUID,
    body: CreateInfraestruturaRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InfraestruturaResponse:
    """Create a new infraestrutura for an escola."""
    svc = EscolaService(db)
    try:
        infra = await svc.create_infraestrutura(
            escola_id=escola_id,
            tenant_id=current_user.tenant_id,
            nome=body.nome,
            tipo=body.tipo,
            capacidade=body.capacidade,
            estado=body.estado,
            observacoes=body.observacoes,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    return InfraestruturaResponse.model_validate(infra)


@router.patch(
    "/escolas/{escola_id}/infraestruturas/{infra_id}",
    response_model=InfraestruturaResponse,
    dependencies=[Depends(require_role("super_admin", "diretor", "secretaria"))],
)
async def update_infraestrutura(
    escola_id: uuid.UUID,
    infra_id: uuid.UUID,
    body: UpdateInfraestruturaRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InfraestruturaResponse:
    """Update an infraestrutura."""
    svc = EscolaService(db)
    fields = body.model_dump(exclude_unset=True)
    try:
        infra = await svc.update_infraestrutura(
            infra_id=infra_id,
            escola_id=escola_id,
            tenant_id=current_user.tenant_id,
            **fields,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return InfraestruturaResponse.model_validate(infra)


@router.delete(
    "/escolas/{escola_id}/infraestruturas/{infra_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("super_admin", "diretor", "secretaria"))],
)
async def delete_infraestrutura(
    escola_id: uuid.UUID,
    infra_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete an infraestrutura."""
    svc = EscolaService(db)
    try:
        await svc.delete_infraestrutura(infra_id, escola_id, current_user.tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e