"""Seed data for the escolas module."""

import asyncio
import os
from datetime import date

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.modules.escolas.infrastructure.models import ConfiguracaoEscola, Escola, Infraestrutura


async def seed_escolas(session: AsyncSession) -> None:
    """Create test escola with infraestruturas for the pilot tenant."""
    # Get the pilot tenant ID
    result = await session.execute(text("SELECT id FROM identity.tenant WHERE nome = 'Escola Piloto SIENA'"))
    row = result.first()
    if row is None:
        print("Tenant 'Escola Piloto SIENA' not found. Run identity seed first.")
        return

    tenant_id = row[0]

    # Check if escola already exists
    existing = await session.execute(
        select(Escola).where(Escola.tenant_id == tenant_id, Escola.deleted_at.is_(None))
    )
    if existing.first():
        print("Escolas seed: escola already exists, skipping.")
        return

    # Create escola
    escola = Escola(
        tenant_id=tenant_id,
        nome="Escola Primária Nº 1 de Luanda",
        codigo_sige="SIGE-LDA-001",
        tipo="publica",
        nivel_ensino="primario",
        provincia="Luanda",
        municipio="Luanda",
        comuna="Ingombota",
        endereco="Rua Major Kanhangulo, Ingombota, Luanda",
        telefone="+244 222 123 456",
        email="ep1luanda@med.gov.ao",
        latitude=-8.8383,
        longitude=13.2344,
    )
    session.add(escola)
    await session.flush()

    # Create default configuration
    config = ConfiguracaoEscola(
        tenant_id=tenant_id,
        escola_id=escola.id,
        num_periodos=3,
        nota_maxima=20,
        nota_minima_aprovacao=10,
    )
    session.add(config)

    # Create infraestruturas
    infras = [
        Infraestrutura(
            tenant_id=tenant_id, escola_id=escola.id,
            nome="Sala 1A", tipo="sala_aula", capacidade=40, estado="operacional",
        ),
        Infraestrutura(
            tenant_id=tenant_id, escola_id=escola.id,
            nome="Sala 1B", tipo="sala_aula", capacidade=40, estado="operacional",
        ),
        Infraestrutura(
            tenant_id=tenant_id, escola_id=escola.id,
            nome="Sala 2A", tipo="sala_aula", capacidade=35, estado="operacional",
        ),
        Infraestrutura(
            tenant_id=tenant_id, escola_id=escola.id,
            nome="Biblioteca", tipo="biblioteca", capacidade=30, estado="operacional",
        ),
        Infraestrutura(
            tenant_id=tenant_id, escola_id=escola.id,
            nome="Cantina", tipo="cantina", capacidade=100, estado="em_reparacao",
        ),
    ]
    for infra in infras:
        session.add(infra)

    await session.commit()
    print(f"Escolas seed: created escola '{escola.nome}' with {len(infras)} infraestruturas.")


async def main() -> None:
    database_url = os.getenv("DATABASE_URL", "postgresql+psycopg://siena:siena@localhost:5432/siena")
    engine = create_async_engine(database_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        await seed_escolas(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())