"""Seed data for the directory module."""

import asyncio
import os
from datetime import date

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.modules.directory.infrastructure.models import (
    Aluno,
    Encarregado,
    Pessoa,
    Professor,
    VinculoAlunoEncarregado,
)


async def seed_directory(session: AsyncSession) -> None:
    """Create test people (alunos, professores, encarregados) for the pilot tenant."""
    # Get the pilot tenant ID
    result = await session.execute(
        text("SELECT id FROM identity.tenant WHERE nome = 'Escola Piloto SIENA'")
    )
    row = result.first()
    if row is None:
        print("Tenant 'Escola Piloto SIENA' not found. Run identity seed first.")
        return

    tenant_id = row[0]

    # Check if directory data already exists
    existing = await session.execute(
        select(Pessoa).where(Pessoa.tenant_id == tenant_id, Pessoa.deleted_at.is_(None))
    )
    if existing.first():
        print("Directory seed: data already exists, skipping.")
        return

    # ── 5 Alunos ────────────────────────────────
    alunos_data = [
        {
            "nome": "Ana Maria da Silva",
            "bi": "007234567LA001",
            "nascimento": date(2012, 3, 15),
            "sexo": "F",
            "n_processo": "ALU-2026-001",
            "ano_ingresso": 2026,
        },
        {
            "nome": "Pedro Manuel João",
            "bi": "007234568LA002",
            "nascimento": date(2011, 7, 22),
            "sexo": "M",
            "n_processo": "ALU-2026-002",
            "ano_ingresso": 2026,
        },
        {
            "nome": "Luísa Fernanda Santos",
            "bi": "007234569LA003",
            "nascimento": date(2012, 1, 10),
            "sexo": "F",
            "n_processo": "ALU-2026-003",
            "ano_ingresso": 2026,
        },
        {
            "nome": "Carlos Alberto Neto",
            "bi": "007234570LA004",
            "nascimento": date(2011, 11, 5),
            "sexo": "M",
            "n_processo": "ALU-2026-004",
            "ano_ingresso": 2026,
        },
        {
            "nome": "Teresa Joaquina Domingos",
            "bi": "007234571LA005",
            "nascimento": date(2012, 6, 18),
            "sexo": "F",
            "n_processo": "ALU-2026-005",
            "ano_ingresso": 2026,
            "necessidades_especiais": True,
        },
    ]

    alunos = []
    for data in alunos_data:
        pessoa = Pessoa(
            tenant_id=tenant_id,
            nome_completo=data["nome"],
            bi_identificacao=data["bi"],
            dt_nascimento=data["nascimento"],
            sexo=data["sexo"],
            nacionalidade="Angolana",
        )
        session.add(pessoa)
        await session.flush()

        aluno = Aluno(
            tenant_id=tenant_id,
            pessoa_id=pessoa.id,
            n_processo=data["n_processo"],
            ano_ingresso=data["ano_ingresso"],
            necessidades_especiais=data.get("necessidades_especiais", False),
        )
        session.add(aluno)
        await session.flush()
        alunos.append(aluno)

    # ── 3 Professores ───────────────────────────
    professores_data = [
        {
            "nome": "José António Ferreira",
            "bi": "005112233LA010",
            "nascimento": date(1985, 4, 20),
            "sexo": "M",
            "codigo": "PROF-001",
            "especialidade": "Matemática",
            "carga": 24,
            "contrato": "efetivo",
            "nivel": "Licenciatura em Matemática",
        },
        {
            "nome": "Maria Helena Sousa",
            "bi": "005112234LA011",
            "nascimento": date(1990, 8, 12),
            "sexo": "F",
            "codigo": "PROF-002",
            "especialidade": "Língua Portuguesa",
            "carga": 22,
            "contrato": "efetivo",
            "nivel": "Licenciatura em Letras",
        },
        {
            "nome": "Francisco Miguel Costa",
            "bi": "005112235LA012",
            "nascimento": date(1992, 2, 28),
            "sexo": "M",
            "codigo": "PROF-003",
            "especialidade": "Ciências Naturais",
            "carga": 20,
            "contrato": "contrato",
            "nivel": "Bacharelato em Biologia",
        },
    ]

    for data in professores_data:
        pessoa = Pessoa(
            tenant_id=tenant_id,
            nome_completo=data["nome"],
            bi_identificacao=data["bi"],
            dt_nascimento=data["nascimento"],
            sexo=data["sexo"],
            nacionalidade="Angolana",
        )
        session.add(pessoa)
        await session.flush()

        professor = Professor(
            tenant_id=tenant_id,
            pessoa_id=pessoa.id,
            codigo_funcional=data["codigo"],
            especialidade=data["especialidade"],
            carga_horaria_semanal=data["carga"],
            tipo_contrato=data["contrato"],
            nivel_academico=data["nivel"],
        )
        session.add(professor)

    # ── 5 Encarregados ──────────────────────────
    encarregados_data = [
        {
            "nome": "Manuel da Silva",
            "bi": "004998877LA020",
            "nascimento": date(1980, 5, 10),
            "sexo": "M",
            "profissao": "Engenheiro Civil",
            "escolaridade": "Licenciatura",
        },
        {
            "nome": "Rosa Maria João",
            "bi": "004998878LA021",
            "nascimento": date(1982, 9, 3),
            "sexo": "F",
            "profissao": "Enfermeira",
            "escolaridade": "Licenciatura",
        },
        {
            "nome": "António Fernando Santos",
            "bi": "004998879LA022",
            "nascimento": date(1978, 12, 25),
            "sexo": "M",
            "profissao": "Comerciante",
            "escolaridade": "12.ª Classe",
        },
        {
            "nome": "Joana Francisca Neto",
            "bi": "004998880LA023",
            "nascimento": date(1983, 3, 7),
            "sexo": "F",
            "profissao": "Professora",
            "escolaridade": "Licenciatura",
        },
        {
            "nome": "Domingos José Domingos",
            "bi": "004998881LA024",
            "nascimento": date(1975, 7, 15),
            "sexo": "M",
            "profissao": "Motorista",
            "escolaridade": "9.ª Classe",
        },
    ]

    encarregados = []
    for data in encarregados_data:
        pessoa = Pessoa(
            tenant_id=tenant_id,
            nome_completo=data["nome"],
            bi_identificacao=data["bi"],
            dt_nascimento=data["nascimento"],
            sexo=data["sexo"],
            nacionalidade="Angolana",
        )
        session.add(pessoa)
        await session.flush()

        encarregado = Encarregado(
            tenant_id=tenant_id,
            pessoa_id=pessoa.id,
            profissao=data["profissao"],
            escolaridade=data["escolaridade"],
        )
        session.add(encarregado)
        await session.flush()
        encarregados.append(encarregado)

    # ── Vínculos Aluno ↔ Encarregado ────────────
    vinculos = [
        # Ana (0) → Manuel da Silva (0) — pai, principal
        VinculoAlunoEncarregado(
            tenant_id=tenant_id,
            aluno_id=alunos[0].id,
            encarregado_id=encarregados[0].id,
            tipo="pai",
            principal=True,
        ),
        # Pedro (1) → Rosa Maria João (1) — mae, principal
        VinculoAlunoEncarregado(
            tenant_id=tenant_id,
            aluno_id=alunos[1].id,
            encarregado_id=encarregados[1].id,
            tipo="mae",
            principal=True,
        ),
        # Luísa (2) → António Santos (2) — pai, principal
        VinculoAlunoEncarregado(
            tenant_id=tenant_id,
            aluno_id=alunos[2].id,
            encarregado_id=encarregados[2].id,
            tipo="pai",
            principal=True,
        ),
        # Carlos (3) → Joana Neto (3) — mae, principal
        VinculoAlunoEncarregado(
            tenant_id=tenant_id,
            aluno_id=alunos[3].id,
            encarregado_id=encarregados[3].id,
            tipo="mae",
            principal=True,
        ),
        # Teresa (4) → Domingos José (4) — pai, principal
        VinculoAlunoEncarregado(
            tenant_id=tenant_id,
            aluno_id=alunos[4].id,
            encarregado_id=encarregados[4].id,
            tipo="pai",
            principal=True,
        ),
        # Ana (0) → Rosa Maria João (1) — tutor (segundo vínculo)
        VinculoAlunoEncarregado(
            tenant_id=tenant_id,
            aluno_id=alunos[0].id,
            encarregado_id=encarregados[1].id,
            tipo="tutor",
            principal=False,
        ),
    ]

    for v in vinculos:
        session.add(v)

    await session.commit()
    print(
        f"Directory seed: created {len(alunos_data)} alunos, "
        f"{len(professores_data)} professores, "
        f"{len(encarregados_data)} encarregados, "
        f"{len(vinculos)} vínculos."
    )


async def main() -> None:
    database_url = os.getenv(
        "DATABASE_URL", "postgresql+psycopg://siena:siena@localhost:5432/siena"
    )
    engine = create_async_engine(database_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        await seed_directory(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())