"""Seed test users for each role so all portals can be tested.

Run with:  python -m scripts.seed_test_users
"""

import asyncio
import os

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.common.utils.password import hash_password
from src.modules.identity.infrastructure.models import (
    Papel,
    Utilizador,
    UtilizadorPapel,
)

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg://siena:siena@localhost:5432/siena"
)

# (username, password, nome_completo, papel, email)
TEST_USERS = [
    ("diretor", "diretor123", "Dr. Manuel Ferreira", "diretor", "diretor@siena.gov.ao"),
    ("secretaria", "secretaria123", "Joana da Silva", "secretaria", "secretaria@siena.gov.ao"),
    ("professor", "professor123", "Prof. Jose Antonio Ferreira", "professor", "professor@siena.gov.ao"),
    ("aluno", "aluno123", "Ana Maria da Silva", "aluno", "aluno@siena.gov.ao"),
    ("encarregado", "encarregado123", "Manuel da Silva", "encarregado", "encarregado@siena.gov.ao"),
]


async def seed_test_users() -> None:
    engine = create_async_engine(DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        # Get pilot tenant
        result = await session.execute(
            text("SELECT id FROM identity.tenant WHERE nome = 'Escola Piloto SIENA'")
        )
        row = result.first()
        if row is None:
            print("Tenant 'Escola Piloto SIENA' not found. Run identity seed first.")
            await engine.dispose()
            return

        tenant_id = row[0]

        # Cache papeis
        papeis_result = await session.execute(select(Papel))
        papeis_map: dict[str, Papel] = {
            p.nome: p for p in papeis_result.scalars().all()
        }

        for username, password, nome, papel_nome, email in TEST_USERS:
            # Check if user already exists
            existing = await session.execute(
                select(Utilizador).where(
                    Utilizador.username == username,
                    Utilizador.tenant_id == tenant_id,
                )
            )
            if existing.scalar_one_or_none():
                print(f"  User '{username}' already exists, skipping.")
                continue

            papel = papeis_map.get(papel_nome)
            if papel is None:
                print(f"  Role '{papel_nome}' not found, skipping user '{username}'.")
                continue

            user = Utilizador(
                tenant_id=tenant_id,
                username=username,
                senha_hash=hash_password(password),
                nome_completo=nome,
                email=email,
            )
            session.add(user)
            await session.flush()

            session.add(
                UtilizadorPapel(
                    utilizador_id=user.id,
                    papel_id=papel.id,
                    tenant_id=tenant_id,
                )
            )
            print(f"  Created user: {username} / {password} (role: {papel_nome})")

        await session.commit()

    await engine.dispose()
    print("\nTest users seed completed!")


if __name__ == "__main__":
    asyncio.run(seed_test_users())
