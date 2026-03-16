"""Seed data for the avaliacoes module."""

import asyncio
import os

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.modules.avaliacoes.infrastructure.models import RegraMedia


async def seed_avaliacoes(session: AsyncSession) -> None:
    """Create test regras de média for the pilot tenant."""
    result = await session.execute(
        text("SELECT id FROM identity.tenant WHERE nome = 'Escola Piloto SIENA'")
    )
    row = result.first()
    if row is None:
        print("Tenant 'Escola Piloto SIENA' not found.")
        return

    tenant_id = row[0]

    existing = await session.execute(
        select(RegraMedia).where(
            RegraMedia.tenant_id == tenant_id, RegraMedia.deleted_at.is_(None)
        )
    )
    if existing.first():
        print("Avaliacoes seed: data already exists, skipping.")
        return

    regras = [
        RegraMedia(
            tenant_id=tenant_id,
            nivel="primario",
            formula="media_ponderada(notas, pesos)",
            minimo_aprovacao=10,
            politica_recuperacao="Exame de recurso se média < 10",
        ),
        RegraMedia(
            tenant_id=tenant_id,
            nivel="secundario_1ciclo",
            formula="media_ponderada(notas, pesos)",
            minimo_aprovacao=10,
            politica_recuperacao="Exame de recurso se média < 10. Máximo 2 disciplinas em recurso.",
        ),
        RegraMedia(
            tenant_id=tenant_id,
            nivel="secundario_2ciclo",
            formula="media_ponderada(notas, pesos)",
            minimo_aprovacao=10,
            politica_recuperacao="Exame nacional obrigatório. Recurso se média < 10.",
        ),
    ]

    for r in regras:
        session.add(r)

    await session.commit()
    print(f"Avaliacoes seed: created {len(regras)} regras de média.")


async def main() -> None:
    database_url = os.getenv(
        "DATABASE_URL", "postgresql+psycopg://siena:siena@localhost:5432/siena"
    )
    engine = create_async_engine(database_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        await seed_avaliacoes(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
