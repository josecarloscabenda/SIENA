"""Seed data for the academico module."""

import asyncio
import os
from datetime import time

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.modules.academico.infrastructure.models import (
    Curriculo,
    Disciplina,
    HorarioAula,
    Turma,
)
from src.modules.directory.infrastructure.models import Professor
from src.modules.escolas.infrastructure.models import AnoLetivo


async def seed_academico(session: AsyncSession) -> None:
    """Create test currículo, disciplinas, turmas and horários."""
    result = await session.execute(
        text("SELECT id FROM identity.tenant WHERE nome = 'Escola Piloto SIENA'")
    )
    row = result.first()
    if row is None:
        print("Tenant 'Escola Piloto SIENA' not found.")
        return

    tenant_id = row[0]

    # Check existing
    existing = await session.execute(
        select(Curriculo).where(
            Curriculo.tenant_id == tenant_id, Curriculo.deleted_at.is_(None)
        )
    )
    if existing.first():
        print("Academico seed: data already exists, skipping.")
        return

    # Get ano letivo ativo
    ano_result = await session.execute(
        select(AnoLetivo).where(
            AnoLetivo.tenant_id == tenant_id,
            AnoLetivo.ativo.is_(True),
            AnoLetivo.deleted_at.is_(None),
        )
    )
    ano_letivo = ano_result.scalar_one_or_none()
    if ano_letivo is None:
        print("Academico seed: no active ano letivo found.")
        return

    # Get professores
    prof_result = await session.execute(
        select(Professor).where(
            Professor.tenant_id == tenant_id, Professor.deleted_at.is_(None)
        )
    )
    professores = list(prof_result.scalars().all())
    if len(professores) < 3:
        print("Academico seed: need at least 3 professors.")
        return

    # ── Currículo 7.ª classe ────────────────────
    curriculo = Curriculo(
        tenant_id=tenant_id,
        nivel="secundario_1ciclo",
        classe="7.ª",
        ano_letivo_id=ano_letivo.id,
        carga_horaria_total=30,
    )
    session.add(curriculo)
    await session.flush()

    # ── 8 Disciplinas ───────────────────────────
    disciplinas_data = [
        ("Língua Portuguesa", "LP-7", 5),
        ("Matemática", "MAT-7", 5),
        ("Ciências Naturais", "CN-7", 3),
        ("História", "HIST-7", 3),
        ("Geografia", "GEO-7", 3),
        ("Educação Física", "EF-7", 2),
        ("Educação Visual", "EV-7", 2),
        ("Inglês", "ING-7", 3),
    ]

    disciplinas = []
    for nome, codigo, carga in disciplinas_data:
        disc = Disciplina(
            tenant_id=tenant_id,
            nome=nome,
            codigo=codigo,
            curriculo_id=curriculo.id,
            carga_horaria_semanal=carga,
        )
        session.add(disc)
        await session.flush()
        disciplinas.append(disc)

    # ── 2 Turmas ────────────────────────────────
    turma_a = Turma(
        tenant_id=tenant_id,
        nome="7.ª-A",
        classe="7.ª",
        turno="matutino",
        ano_letivo_id=ano_letivo.id,
        capacidade_max=35,
        professor_regente_id=professores[0].id,
        sala="Sala 1A",
    )
    turma_b = Turma(
        tenant_id=tenant_id,
        nome="7.ª-B",
        classe="7.ª",
        turno="matutino",
        ano_letivo_id=ano_letivo.id,
        capacidade_max=35,
        professor_regente_id=professores[1].id,
        sala="Sala 1B",
    )
    session.add(turma_a)
    session.add(turma_b)
    await session.flush()

    # ── Horários para turma A (amostra) ─────────
    horarios = [
        # Segunda
        HorarioAula(
            tenant_id=tenant_id, turma_id=turma_a.id,
            disciplina_id=disciplinas[0].id, professor_id=professores[1].id,
            dia_semana="segunda", hora_inicio=time(7, 30), hora_fim=time(8, 15),
        ),
        HorarioAula(
            tenant_id=tenant_id, turma_id=turma_a.id,
            disciplina_id=disciplinas[1].id, professor_id=professores[0].id,
            dia_semana="segunda", hora_inicio=time(8, 20), hora_fim=time(9, 5),
        ),
        HorarioAula(
            tenant_id=tenant_id, turma_id=turma_a.id,
            disciplina_id=disciplinas[2].id, professor_id=professores[2].id,
            dia_semana="segunda", hora_inicio=time(9, 20), hora_fim=time(10, 5),
        ),
        # Terça
        HorarioAula(
            tenant_id=tenant_id, turma_id=turma_a.id,
            disciplina_id=disciplinas[1].id, professor_id=professores[0].id,
            dia_semana="terca", hora_inicio=time(7, 30), hora_fim=time(8, 15),
        ),
        HorarioAula(
            tenant_id=tenant_id, turma_id=turma_a.id,
            disciplina_id=disciplinas[3].id, professor_id=professores[1].id,
            dia_semana="terca", hora_inicio=time(8, 20), hora_fim=time(9, 5),
        ),
        # Quarta
        HorarioAula(
            tenant_id=tenant_id, turma_id=turma_a.id,
            disciplina_id=disciplinas[0].id, professor_id=professores[1].id,
            dia_semana="quarta", hora_inicio=time(7, 30), hora_fim=time(8, 15),
        ),
        HorarioAula(
            tenant_id=tenant_id, turma_id=turma_a.id,
            disciplina_id=disciplinas[7].id, professor_id=professores[2].id,
            dia_semana="quarta", hora_inicio=time(8, 20), hora_fim=time(9, 5),
        ),
    ]

    for h in horarios:
        session.add(h)

    await session.commit()
    print(
        f"Academico seed: created currículo 7.ª classe, "
        f"{len(disciplinas)} disciplinas, 2 turmas, {len(horarios)} horários."
    )


async def main() -> None:
    database_url = os.getenv(
        "DATABASE_URL", "postgresql+psycopg://siena:siena@localhost:5432/siena"
    )
    engine = create_async_engine(database_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        await seed_academico(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
