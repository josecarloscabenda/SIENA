"""Repository for the escolas module."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.modules.escolas.infrastructure.models import (
    AnoLetivo,
    ConfiguracaoEscola,
    Escola,
    Infraestrutura,
)


class EscolasRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # --- Escola ---

    async def get_escola(self, escola_id: uuid.UUID, tenant_id: uuid.UUID) -> Escola | None:
        stmt = (
            select(Escola)
            .options(
                selectinload(Escola.anos_letivos),
                selectinload(Escola.infraestruturas),
                selectinload(Escola.configuracao),
            )
            .where(Escola.id == escola_id, Escola.tenant_id == tenant_id, Escola.deleted_at.is_(None))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_escolas(
        self,
        tenant_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        provincia: str | None = None,
        municipio: str | None = None,
    ) -> tuple[list[Escola], int]:
        base = select(Escola).where(Escola.tenant_id == tenant_id, Escola.deleted_at.is_(None))
        if provincia:
            base = base.where(Escola.provincia == provincia)
        if municipio:
            base = base.where(Escola.municipio == municipio)

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = base.order_by(Escola.nome).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def create_escola(self, escola: Escola) -> Escola:
        self.db.add(escola)
        await self.db.flush()
        await self.db.refresh(escola)
        return escola

    async def get_escola_by_codigo_sige(self, codigo_sige: str) -> Escola | None:
        stmt = select(Escola).where(Escola.codigo_sige == codigo_sige, Escola.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # --- Ano Letivo ---

    async def get_ano_letivo_ativo(self, escola_id: uuid.UUID, tenant_id: uuid.UUID) -> AnoLetivo | None:
        stmt = select(AnoLetivo).where(
            AnoLetivo.escola_id == escola_id,
            AnoLetivo.tenant_id == tenant_id,
            AnoLetivo.ativo.is_(True),
            AnoLetivo.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_ano_letivo(self, ano: AnoLetivo) -> AnoLetivo:
        self.db.add(ano)
        await self.db.flush()
        await self.db.refresh(ano)
        return ano

    async def deactivate_anos_letivos(self, escola_id: uuid.UUID, tenant_id: uuid.UUID) -> None:
        stmt = select(AnoLetivo).where(
            AnoLetivo.escola_id == escola_id,
            AnoLetivo.tenant_id == tenant_id,
            AnoLetivo.ativo.is_(True),
        )
        result = await self.db.execute(stmt)
        for ano in result.scalars().all():
            ano.ativo = False

    # --- Infraestrutura ---

    async def list_infraestruturas(self, escola_id: uuid.UUID, tenant_id: uuid.UUID) -> list[Infraestrutura]:
        stmt = (
            select(Infraestrutura)
            .where(
                Infraestrutura.escola_id == escola_id,
                Infraestrutura.tenant_id == tenant_id,
                Infraestrutura.deleted_at.is_(None),
            )
            .order_by(Infraestrutura.nome)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # --- Configuração ---

    async def get_configuracao(self, escola_id: uuid.UUID, tenant_id: uuid.UUID) -> ConfiguracaoEscola | None:
        stmt = select(ConfiguracaoEscola).where(
            ConfiguracaoEscola.escola_id == escola_id,
            ConfiguracaoEscola.tenant_id == tenant_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
