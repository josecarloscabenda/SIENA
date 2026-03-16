"""Seed data for the enrollment module."""

import asyncio
import os
from datetime import date

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.modules.directory.infrastructure.models import Aluno
from src.modules.enrollment.infrastructure.models import Matricula
from src.modules.escolas.infrastructure.models import AnoLetivo


async def seed_enrollment(session: AsyncSession) -> None:
    """Create test matrículas for the pilot tenant."""
    # Get the pilot tenant ID
    result = await session.execute(
        text("SELECT id FROM identity.tenant WHERE nome = 'Escola Piloto SIENA'")
    )
    row = result.first()
    if row is None:
        print("Tenant 'Escola Piloto SIENA' not found. Run identity seed first.")
        return

    tenant_id = row[0]

    # Check if enrollment data already exists
    existing = await session.execute(
        select(Matricula).where(
            Matricula.tenant_id == tenant_id, Matricula.deleted_at.is_(None)
        )
    )
    if existing.first():
        print("Enrollment seed: data already exists, skipping.")
        return

    # Get the active ano letivo
    ano_result = await session.execute(
        select(AnoLetivo).where(
            AnoLetivo.tenant_id == tenant_id,
            AnoLetivo.ativo.is_(True),
            AnoLetivo.deleted_at.is_(None),
        )
    )
    ano_letivo = ano_result.scalar_one_or_none()
    if ano_letivo is None:
        print("Enrollment seed: no active ano letivo found. Run escolas seed first.")
        return

    # Get all alunos
    alunos_result = await session.execute(
        select(Aluno).where(
            Aluno.tenant_id == tenant_id, Aluno.deleted_at.is_(None)
        )
    )
    alunos = list(alunos_result.scalars().all())
    if not alunos:
        print("Enrollment seed: no alunos found. Run directory seed first.")
        return

    # Create 5 matrículas aprovadas (uma por aluno)
    classes = ["7.ª", "7.ª", "7.ª", "8.ª", "8.ª"]
    turnos = ["matutino", "matutino", "matutino", "vespertino", "matutino"]

    for i, aluno in enumerate(alunos[:5]):
        matricula = Matricula(
            tenant_id=tenant_id,
            aluno_id=aluno.id,
            ano_letivo_id=ano_letivo.id,
            classe=classes[i] if i < len(classes) else "7.ª",
            turno=turnos[i] if i < len(turnos) else "matutino",
            estado="aprovada",
            data_pedido=date(2026, 1, 15),
            data_aprovacao=date(2026, 2, 1),
        )
        session.add(matricula)

    await session.commit()
    print(f"Enrollment seed: created {min(len(alunos), 5)} matrículas aprovadas.")


async def main() -> None:
    database_url = os.getenv(
        "DATABASE_URL", "postgresql+psycopg://siena:siena@localhost:5432/siena"
    )
    engine = create_async_engine(database_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        await seed_enrollment(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
