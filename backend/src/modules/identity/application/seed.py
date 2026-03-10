"""Seed script: creates default roles, a test tenant, and a super_admin user."""

import asyncio
import os

from sqlalchemy import select

from src.common.utils.password import hash_password
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.common.database.base import Base  # noqa: F401
from src.modules.identity.infrastructure.models import Papel, Tenant, Utilizador, UtilizadorPapel

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://siena:siena@localhost:5432/siena")

DEFAULT_ROLES = [
    ("super_admin", "Administrador da plataforma — acesso total"),
    ("platform_admin", "Suporte técnico — leitura em todos os tenants"),
    ("diretor", "Diretor de escola — gestão completa da escola"),
    ("secretaria", "Secretária — matrículas, pessoas, financeiro"),
    ("professor", "Professor — notas, faltas, diário das suas turmas"),
    ("encarregado", "Encarregado de educação — leitura do educando"),
    ("aluno", "Aluno — leitura do próprio boletim e horário"),
    ("gestor_municipal", "Gestor municipal — dados consolidados do município"),
    ("gestor_provincial", "Gestor provincial — dados consolidados da província"),
    ("gestor_nacional", "Gestor nacional — exportações MED/INE"),
]


async def seed() -> None:
    engine = create_async_engine(DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        await _seed_roles(session)
        await _seed_tenant_and_admin(session)
        await session.commit()

    await engine.dispose()
    print("Seed completed successfully!")


async def _seed_roles(session: AsyncSession) -> None:
    for nome, descricao in DEFAULT_ROLES:
        existing = await session.execute(select(Papel).where(Papel.nome == nome))
        if existing.scalar_one_or_none() is None:
            session.add(Papel(nome=nome, descricao=descricao))
            print(f"  Created role: {nome}")
        else:
            print(f"  Role already exists: {nome}")
    await session.flush()


async def _seed_tenant_and_admin(session: AsyncSession) -> None:
    # Check if test tenant exists
    result = await session.execute(select(Tenant).where(Tenant.nome == "Escola Piloto SIENA"))
    tenant = result.scalar_one_or_none()

    if tenant is None:
        tenant = Tenant(nome="Escola Piloto SIENA", estado="ativo", plano="completo")
        session.add(tenant)
        await session.flush()
        print(f"  Created tenant: {tenant.nome} (id: {tenant.id})")
    else:
        print(f"  Tenant already exists: {tenant.nome} (id: {tenant.id})")

    # Check if super_admin exists
    result = await session.execute(
        select(Utilizador).where(
            Utilizador.username == "admin",
            Utilizador.tenant_id == tenant.id,
        )
    )
    admin = result.scalar_one_or_none()

    if admin is None:
        admin = Utilizador(
            tenant_id=tenant.id,
            username="admin",
            senha_hash=hash_password("admin123"),
            nome_completo="Administrador SIENA",
            email="admin@siena.gov.ao",
        )
        session.add(admin)
        await session.flush()
        print(f"  Created user: admin (id: {admin.id})")

        # Assign super_admin role
        papel_result = await session.execute(select(Papel).where(Papel.nome == "super_admin"))
        papel = papel_result.scalar_one()
        session.add(
            UtilizadorPapel(
                utilizador_id=admin.id,
                papel_id=papel.id,
                tenant_id=tenant.id,
            )
        )
        print("  Assigned role: super_admin → admin")
    else:
        print(f"  User already exists: admin (id: {admin.id})")


if __name__ == "__main__":
    asyncio.run(seed())
