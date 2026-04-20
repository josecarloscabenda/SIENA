"""Repository for identity module — database access layer."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.modules.identity.infrastructure.models import Papel, Tenant, Utilizador, UtilizadorPapel


class IdentityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # --- Tenant ---
    async def get_tenant(self, tenant_id: uuid.UUID) -> Tenant | None:
        return await self.session.get(Tenant, tenant_id)

    async def get_tenant_by_slug(self, slug: str) -> Tenant | None:
        stmt = select(Tenant).where(
            Tenant.slug == slug,
            Tenant.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_public_tenants(self) -> list[Tenant]:
        """Lista tenants activos para selector público de login."""
        stmt = (
            select(Tenant)
            .where(Tenant.estado == "ativo", Tenant.deleted_at.is_(None))
            .order_by(Tenant.nome)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_tenant(self, tenant: Tenant) -> Tenant:
        self.session.add(tenant)
        await self.session.flush()
        return tenant

    # --- Utilizador ---
    async def get_user_by_username(self, username: str, tenant_id: uuid.UUID) -> Utilizador | None:
        stmt = (
            select(Utilizador)
            .options(selectinload(Utilizador.papeis).selectinload(UtilizadorPapel.papel))
            .where(
                Utilizador.username == username,
                Utilizador.tenant_id == tenant_id,
                Utilizador.deleted_at.is_(None),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: uuid.UUID) -> Utilizador | None:
        stmt = (
            select(Utilizador)
            .options(selectinload(Utilizador.papeis).selectinload(UtilizadorPapel.papel))
            .where(Utilizador.id == user_id, Utilizador.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_users(self, tenant_id: uuid.UUID, offset: int = 0, limit: int = 20) -> tuple[list[Utilizador], int]:
        base = select(Utilizador).where(
            Utilizador.tenant_id == tenant_id,
            Utilizador.deleted_at.is_(None),
        )
        count_result = await self.session.execute(
            select(Utilizador.id).where(
                Utilizador.tenant_id == tenant_id,
                Utilizador.deleted_at.is_(None),
            )
        )
        total = len(count_result.all())

        stmt = (
            base.options(selectinload(Utilizador.papeis).selectinload(UtilizadorPapel.papel))
            .offset(offset)
            .limit(limit)
            .order_by(Utilizador.nome_completo)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all()), total

    async def create_user(self, user: Utilizador) -> Utilizador:
        self.session.add(user)
        await self.session.flush()
        return user

    # --- Papel ---
    async def get_papel_by_nome(self, nome: str) -> Papel | None:
        stmt = select(Papel).where(Papel.nome == nome)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_papeis(self) -> list[Papel]:
        stmt = select(Papel).where(Papel.deleted_at.is_(None)).order_by(Papel.nome)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_papel(self, papel: Papel) -> Papel:
        self.session.add(papel)
        await self.session.flush()
        return papel

    # --- UtilizadorPapel ---
    async def assign_role(self, link: UtilizadorPapel) -> UtilizadorPapel:
        self.session.add(link)
        await self.session.flush()
        return link
