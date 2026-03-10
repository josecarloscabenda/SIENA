"""FastAPI router for the identity module."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.auth.middleware import CurrentUser, get_current_user
from src.common.auth.rbac import require_role
from src.common.database.session import get_db
from src.modules.identity.api.dtos import (
    CreateUserRequest,
    LoginRequest,
    PapelResponse,
    RefreshRequest,
    TokenResponse,
    UpdateUserRequest,
    UserListResponse,
    UserResponse,
)
from src.modules.identity.application.services import AuthService, UserService
from src.modules.identity.infrastructure.repository import IdentityRepository

router = APIRouter()


# --- Helper to convert User model to response ---
def _user_to_response(user) -> UserResponse:  # noqa: ANN001
    return UserResponse(
        id=user.id,
        tenant_id=user.tenant_id,
        username=user.username,
        nome_completo=user.nome_completo,
        email=user.email,
        ativo=user.ativo,
        papeis=[up.papel.nome for up in user.papeis if up.ativo],
        ultimo_login=user.ultimo_login,
        created_at=user.created_at,
    )


# ============================================================
# AUTH
# ============================================================


@router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Authenticate user and return JWT tokens."""
    auth = AuthService(db)
    try:
        result = await auth.login(body.username, body.password, body.tenant_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
    return TokenResponse(**result)


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Refresh access token using a valid refresh token."""
    auth = AuthService(db)
    try:
        result = await auth.refresh(body.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e
    return TokenResponse(**result)


@router.get("/auth/me", response_model=UserResponse)
async def me(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Get the currently authenticated user's profile."""
    svc = UserService(db)
    user = await svc.get_user(current_user.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilizador não encontrado")
    return _user_to_response(user)


# ============================================================
# USERS
# ============================================================


@router.get(
    "/users",
    response_model=UserListResponse,
    dependencies=[Depends(require_role("super_admin", "diretor"))],
)
async def list_users(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> UserListResponse:
    """List users for the current tenant."""
    svc = UserService(db)
    users, total = await svc.list_users(current_user.tenant_id, offset, limit)
    return UserListResponse(
        total=total,
        offset=offset,
        limit=limit,
        items=[_user_to_response(u) for u in users],
    )


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("super_admin", "diretor"))],
)
async def create_user(
    body: CreateUserRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Create a new user in the current tenant."""
    svc = UserService(db)
    try:
        user = await svc.create_user(
            tenant_id=current_user.tenant_id,
            username=body.username,
            password=body.password,
            nome_completo=body.nome_completo,
            email=body.email,
            papel_nome=body.papel,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    # Reload to get papeis relationship
    user = await svc.get_user(user.id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao criar utilizador")
    return _user_to_response(user)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Get a user by ID."""
    svc = UserService(db)
    user = await svc.get_user(user_id)
    if user is None or user.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilizador não encontrado")
    return _user_to_response(user)


@router.patch(
    "/users/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_role("super_admin", "diretor"))],
)
async def update_user(
    user_id: uuid.UUID,
    body: UpdateUserRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Update a user."""
    svc = UserService(db)
    try:
        user = await svc.update_user(
            user_id=user_id,
            nome_completo=body.nome_completo,
            email=body.email,
            ativo=body.ativo,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

    if user.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilizador não encontrado")
    return _user_to_response(user)


# ============================================================
# ROLES
# ============================================================


@router.get("/roles", response_model=list[PapelResponse])
async def list_roles(
    _current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[PapelResponse]:
    """List all available roles."""
    repo = IdentityRepository(db)
    papeis = await repo.list_papeis()
    return [PapelResponse.model_validate(p) for p in papeis]
