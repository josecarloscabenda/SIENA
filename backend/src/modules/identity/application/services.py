"""Application services for the identity module."""

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.common.utils.password import hash_password, verify_password
from src.common.auth.jwt import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from src.modules.identity.infrastructure.models import Utilizador, UtilizadorPapel
from src.modules.identity.infrastructure.repository import IdentityRepository


class AuthService:
    """Handles authentication: login, token refresh, logout."""

    def __init__(self, session: AsyncSession) -> None:
        self.repo = IdentityRepository(session)

    async def resolve_tenant_id(
        self, tenant_id: uuid.UUID | None, tenant_slug: str | None
    ) -> uuid.UUID:
        """Accept either tenant_id OR tenant_slug and return the UUID."""
        if tenant_id is not None:
            return tenant_id
        if tenant_slug:
            tenant = await self.repo.get_tenant_by_slug(tenant_slug)
            if tenant is None:
                raise ValueError(f"Escola '{tenant_slug}' não encontrada")
            return tenant.id
        raise ValueError("Identificador da escola (tenant_id ou tenant_slug) é obrigatório")

    async def login(self, username: str, password: str, tenant_id: uuid.UUID) -> dict:
        user = await self.repo.get_user_by_username(username, tenant_id)

        if user is None or not verify_password(password, user.senha_hash):
            raise ValueError("Credenciais inválidas")

        if not user.ativo:
            raise ValueError("Utilizador desactivado")

        papeis = [up.papel.nome for up in user.papeis if up.ativo]

        access_token = create_access_token(user.id, user.tenant_id, papeis)
        refresh_token = create_refresh_token(user.id, user.tenant_id)

        user.ultimo_login = datetime.now(UTC)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    async def refresh(self, refresh_token_str: str) -> dict:
        payload = decode_token(refresh_token_str)
        if payload is None or payload.get("type") != "refresh":
            raise ValueError("Refresh token inválido")

        user_id = uuid.UUID(payload["sub"])
        tenant_id = uuid.UUID(payload["tenant_id"])

        user = await self.repo.get_user_by_id(user_id)
        if user is None or not user.ativo:
            raise ValueError("Utilizador não encontrado ou desactivado")

        papeis = [up.papel.nome for up in user.papeis if up.ativo]

        access_token = create_access_token(user.id, tenant_id, papeis)
        new_refresh = create_refresh_token(user.id, tenant_id)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }


class UserService:
    """Handles user CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.repo = IdentityRepository(session)

    async def create_user(
        self,
        tenant_id: uuid.UUID,
        username: str,
        password: str,
        nome_completo: str,
        email: str | None,
        papel_nome: str,
    ) -> Utilizador:
        existing = await self.repo.get_user_by_username(username, tenant_id)
        if existing is not None:
            raise ValueError(f"Username '{username}' já existe neste tenant")

        papel = await self.repo.get_papel_by_nome(papel_nome)
        if papel is None:
            raise ValueError(f"Papel '{papel_nome}' não encontrado")

        user = Utilizador(
            tenant_id=tenant_id,
            username=username,
            senha_hash=hash_password(password),
            nome_completo=nome_completo,
            email=email,
        )
        user = await self.repo.create_user(user)

        link = UtilizadorPapel(
            utilizador_id=user.id,
            papel_id=papel.id,
            tenant_id=tenant_id,
        )
        await self.repo.assign_role(link)

        return user

    async def get_user(self, user_id: uuid.UUID) -> Utilizador | None:
        return await self.repo.get_user_by_id(user_id)

    async def list_users(self, tenant_id: uuid.UUID, offset: int = 0, limit: int = 20) -> tuple[list[Utilizador], int]:
        return await self.repo.list_users(tenant_id, offset, limit)

    async def update_user(
        self,
        user_id: uuid.UUID,
        nome_completo: str | None = None,
        email: str | None = None,
        ativo: bool | None = None,
    ) -> Utilizador:
        user = await self.repo.get_user_by_id(user_id)
        if user is None:
            raise ValueError("Utilizador não encontrado")

        if nome_completo is not None:
            user.nome_completo = nome_completo
        if email is not None:
            user.email = email
        if ativo is not None:
            user.ativo = ativo

        return user
