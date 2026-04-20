"""Repository for the avaliacoes module."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.modules.academico.infrastructure.models import Disciplina, Turma
from src.modules.avaliacoes.infrastructure.models import (
    Avaliacao,
    Boletim,
    Falta,
    Nota,
    RegraMedia,
)
from src.modules.directory.infrastructure.models import Aluno, Pessoa


def _attach(obj, **kwargs):
    for k, v in kwargs.items():
        setattr(obj, k, v)
    return obj


class AvaliacoesRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Avaliação ───────────────────────────────

    async def get_avaliacao(
        self, avaliacao_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Avaliacao | None:
        stmt = (
            select(
                Avaliacao,
                Turma.nome.label("turma_nome"),
                Disciplina.nome.label("disciplina_nome"),
            )
            .options(selectinload(Avaliacao.notas))
            .outerjoin(Turma, Turma.id == Avaliacao.turma_id)
            .outerjoin(Disciplina, Disciplina.id == Avaliacao.disciplina_id)
            .where(
                Avaliacao.id == avaliacao_id,
                Avaliacao.tenant_id == tenant_id,
                Avaliacao.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        row = result.first()
        if row is None:
            return None
        avaliacao = _attach(
            row.Avaliacao, turma_nome=row.turma_nome, disciplina_nome=row.disciplina_nome
        )
        if avaliacao.notas:
            await self._enrich_notas(avaliacao.notas)
        return avaliacao

    async def list_avaliacoes(
        self,
        tenant_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        turma_id: uuid.UUID | None = None,
        disciplina_id: uuid.UUID | None = None,
        periodo: int | None = None,
    ) -> tuple[list[Avaliacao], int]:
        filters = [Avaliacao.tenant_id == tenant_id, Avaliacao.deleted_at.is_(None)]
        if turma_id:
            filters.append(Avaliacao.turma_id == turma_id)
        if disciplina_id:
            filters.append(Avaliacao.disciplina_id == disciplina_id)
        if periodo:
            filters.append(Avaliacao.periodo == periodo)

        count_stmt = select(func.count(Avaliacao.id)).where(*filters)
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = (
            select(
                Avaliacao,
                Turma.nome.label("turma_nome"),
                Disciplina.nome.label("disciplina_nome"),
            )
            .outerjoin(Turma, Turma.id == Avaliacao.turma_id)
            .outerjoin(Disciplina, Disciplina.id == Avaliacao.disciplina_id)
            .where(*filters)
            .order_by(Avaliacao.data.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        items = [
            _attach(
                row.Avaliacao,
                turma_nome=row.turma_nome,
                disciplina_nome=row.disciplina_nome,
            )
            for row in result.all()
        ]
        return items, total

    async def create_avaliacao(self, avaliacao: Avaliacao) -> Avaliacao:
        self.db.add(avaliacao)
        await self.db.flush()
        await self.db.refresh(avaliacao)
        return avaliacao

    async def _enrich_notas(self, notas: list[Nota]) -> None:
        """Populate aluno_nome and aluno_n_processo on notas."""
        if not notas:
            return
        aluno_ids = {n.aluno_id for n in notas}
        res = await self.db.execute(
            select(Aluno.id, Aluno.n_processo, Pessoa.nome_completo)
            .join(Pessoa, Pessoa.id == Aluno.pessoa_id)
            .where(Aluno.id.in_(aluno_ids))
        )
        aluno_map = {r.id: (r.n_processo, r.nome_completo) for r in res.all()}
        for n in notas:
            info = aluno_map.get(n.aluno_id)
            n.aluno_n_processo = info[0] if info else None  # type: ignore[attr-defined]
            n.aluno_nome = info[1] if info else None  # type: ignore[attr-defined]

    async def _enrich_faltas(self, faltas: list[Falta]) -> None:
        """Populate aluno_nome, turma_nome, disciplina_nome on faltas."""
        if not faltas:
            return
        aluno_ids = {f.aluno_id for f in faltas}
        turma_ids = {f.turma_id for f in faltas}
        disc_ids = {f.disciplina_id for f in faltas}

        aluno_map: dict[uuid.UUID, str] = {}
        if aluno_ids:
            res = await self.db.execute(
                select(Aluno.id, Pessoa.nome_completo)
                .join(Pessoa, Pessoa.id == Aluno.pessoa_id)
                .where(Aluno.id.in_(aluno_ids))
            )
            aluno_map = {r.id: r.nome_completo for r in res.all()}

        turma_map: dict[uuid.UUID, str] = {}
        if turma_ids:
            res = await self.db.execute(
                select(Turma.id, Turma.nome).where(Turma.id.in_(turma_ids))
            )
            turma_map = {r.id: r.nome for r in res.all()}

        disc_map: dict[uuid.UUID, str] = {}
        if disc_ids:
            res = await self.db.execute(
                select(Disciplina.id, Disciplina.nome).where(Disciplina.id.in_(disc_ids))
            )
            disc_map = {r.id: r.nome for r in res.all()}

        for f in faltas:
            f.aluno_nome = aluno_map.get(f.aluno_id)  # type: ignore[attr-defined]
            f.turma_nome = turma_map.get(f.turma_id)  # type: ignore[attr-defined]
            f.disciplina_nome = disc_map.get(f.disciplina_id)  # type: ignore[attr-defined]

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
        notas = list(result.scalars().all())
        await self._enrich_notas(notas)
        return notas

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
        notas = list(result.scalars().all())
        await self._enrich_notas(notas)
        return notas

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
        notas = list(result.scalars().all())
        await self._enrich_notas(notas)
        return notas

    async def create_nota(self, nota: Nota) -> Nota:
        self.db.add(nota)
        await self.db.flush()
        await self.db.refresh(nota)
        await self._enrich_notas([nota])
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
        faltas = list(result.scalars().all())
        await self._enrich_faltas(faltas)
        return faltas

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
