"""Repository for the avaliacoes module."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.modules.avaliacoes.infrastructure.models import (
    Avaliacao,
    Boletim,
    Falta,
    Nota,
    RegraMedia,
)


class AvaliacoesRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Avaliação ───────────────────────────────

    async def get_avaliacao(
        self, avaliacao_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Avaliacao | None:
        stmt = (
            select(Avaliacao)
            .options(selectinload(Avaliacao.notas))
            .where(
                Avaliacao.id == avaliacao_id,
                Avaliacao.tenant_id == tenant_id,
                Avaliacao.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_avaliacoes(
        self,
        tenant_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        turma_id: uuid.UUID | None = None,
        disciplina_id: uuid.UUID | None = None,
        periodo: int | None = None,
    ) -> tuple[list[Avaliacao], int]:
        base = select(Avaliacao).where(
            Avaliacao.tenant_id == tenant_id, Avaliacao.deleted_at.is_(None)
        )
        if turma_id:
            base = base.where(Avaliacao.turma_id == turma_id)
        if disciplina_id:
            base = base.where(Avaliacao.disciplina_id == disciplina_id)
        if periodo:
            base = base.where(Avaliacao.periodo == periodo)

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = base.order_by(Avaliacao.data.desc()).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def create_avaliacao(self, avaliacao: Avaliacao) -> Avaliacao:
        self.db.add(avaliacao)
        await self.db.flush()
        await self.db.refresh(avaliacao)
        return avaliacao

    # ── Nota ────────────────────────────────────

    async def get_nota(
        self, nota_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Nota | None:
        stmt = select(Nota).where(
            Nota.id == nota_id,
            Nota.tenant_id == tenant_id,
            Nota.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_nota_existente(
        self, avaliacao_id: uuid.UUID, aluno_id: uuid.UUID
    ) -> Nota | None:
        stmt = select(Nota).where(
            Nota.avaliacao_id == avaliacao_id,
            Nota.aluno_id == aluno_id,
            Nota.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_notas_avaliacao(
        self, avaliacao_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[Nota]:
        stmt = (
            select(Nota)
            .where(
                Nota.avaliacao_id == avaliacao_id,
                Nota.tenant_id == tenant_id,
                Nota.deleted_at.is_(None),
            )
            .order_by(Nota.created_at)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_notas_aluno(
        self, aluno_id: uuid.UUID, tenant_id: uuid.UUID, periodo: int | None = None
    ) -> list[Nota]:
        stmt = (
            select(Nota)
            .join(Nota.avaliacao)
            .where(
                Nota.aluno_id == aluno_id,
                Nota.tenant_id == tenant_id,
                Nota.deleted_at.is_(None),
            )
        )
        if periodo:
            stmt = stmt.where(Avaliacao.periodo == periodo)
        stmt = stmt.order_by(Avaliacao.data)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_notas_turma(
        self, turma_id: uuid.UUID, tenant_id: uuid.UUID, periodo: int | None = None
    ) -> list[Nota]:
        stmt = (
            select(Nota)
            .join(Nota.avaliacao)
            .where(
                Avaliacao.turma_id == turma_id,
                Nota.tenant_id == tenant_id,
                Nota.deleted_at.is_(None),
            )
        )
        if periodo:
            stmt = stmt.where(Avaliacao.periodo == periodo)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_nota(self, nota: Nota) -> Nota:
        self.db.add(nota)
        await self.db.flush()
        await self.db.refresh(nota)
        return nota

    # ── Falta ───────────────────────────────────

    async def list_faltas_aluno(
        self,
        aluno_id: uuid.UUID,
        tenant_id: uuid.UUID,
        disciplina_id: uuid.UUID | None = None,
        tipo: str | None = None,
    ) -> list[Falta]:
        base = select(Falta).where(
            Falta.aluno_id == aluno_id,
            Falta.tenant_id == tenant_id,
            Falta.deleted_at.is_(None),
        )
        if disciplina_id:
            base = base.where(Falta.disciplina_id == disciplina_id)
        if tipo:
            base = base.where(Falta.tipo == tipo)
        stmt = base.order_by(Falta.data.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_faltas_aluno(
        self, aluno_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> dict:
        """Conta faltas por tipo e por disciplina."""
        faltas = await self.list_faltas_aluno(aluno_id, tenant_id)
        total = len(faltas)
        justificadas = sum(1 for f in faltas if f.tipo == "justificada")
        injustificadas = total - justificadas

        por_disc: dict[uuid.UUID, int] = {}
        for f in faltas:
            por_disc[f.disciplina_id] = por_disc.get(f.disciplina_id, 0) + 1

        return {
            "total": total,
            "justificadas": justificadas,
            "injustificadas": injustificadas,
            "por_disciplina": [
                {"disciplina_id": str(d_id), "total": cnt}
                for d_id, cnt in por_disc.items()
            ],
        }

    async def create_falta(self, falta: Falta) -> Falta:
        self.db.add(falta)
        await self.db.flush()
        await self.db.refresh(falta)
        return falta
