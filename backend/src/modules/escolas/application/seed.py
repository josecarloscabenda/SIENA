"""Seed data for the escolas module."""

import asyncio
import os
from datetime import date

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.modules.escolas.infrastructure.models import (
    AnoLetivo,
    ConfiguracaoEscola,
    Escola,
    Infraestrutura,
)


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
    existing_escola = existing.scalar_one_or_none()
    if existing_escola is not None:
        # Backfill ano_letivo if missing (older DBs created without it)
        ano_check = await session.execute(
            select(AnoLetivo).where(
                AnoLetivo.escola_id == existing_escola.id,
                AnoLetivo.deleted_at.is_(None),
            )
        )
        if ano_check.first() is None:
            session.add(
                AnoLetivo(
                    tenant_id=tenant_id,
                    escola_id=existing_escola.id,
                    ano=2026,
                    designacao="2026/2027",
                    data_inicio=date(2026, 9, 1),
                    data_fim=date(2027, 7, 31),
                    ativo=True,
                )
            )
            await session.commit()
            print(
                f"Escolas seed: escola existed without ano_letivo — backfilled '2026/2027' (ativo)."
            )
        else:
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

    # Create default active ano_letivo (required by enrollment + academico seeds)
    ano_letivo = AnoLetivo(
        tenant_id=tenant_id,
        escola_id=escola.id,
        ano=2026,
        designacao="2026/2027",
        data_inicio=date(2026, 9, 1),
        data_fim=date(2027, 7, 31),
        ativo=True,
    )
    session.add(ano_letivo)

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
    print(
        f"Escolas seed: created escola '{escola.nome}' with {len(infras)} infraestruturas "
        f"and ano_letivo '{ano_letivo.designacao}' (ativo)."
    )


async def main() -> None:
    database_url = os.getenv("DATABASE_URL", "postgresql+psycopg://siena:siena@localhost:5432/siena")
    engine = create_async_engine(database_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        await seed_escolas(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())