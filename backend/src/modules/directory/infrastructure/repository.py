"""Repository for the directory module."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.modules.directory.infrastructure.models import (
    Aluno,
    Encarregado,
    Funcionario,
    Pessoa,
    Professor,
    VinculoAlunoEncarregado,
)


class DirectoryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Pessoa ──────────────────────────────────

    async def get_pessoa(self, pessoa_id: uuid.UUID, tenant_id: uuid.UUID) -> Pessoa | None:
        stmt = select(Pessoa).where(
            Pessoa.id == pessoa_id,
            Pessoa.tenant_id == tenant_id,
            Pessoa.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pessoa_by_bi(self, tenant_id: uuid.UUID, bi: str) -> Pessoa | None:
        stmt = select(Pessoa).where(
            Pessoa.tenant_id == tenant_id,
            Pessoa.bi_identificacao == bi,
            Pessoa.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_pessoa(self, pessoa: Pessoa) -> Pessoa:
        self.db.add(pessoa)
        await self.db.flush()
        await self.db.refresh(pessoa)
        return pessoa

    # ── Aluno ───────────────────────────────────

    async def get_aluno(self, aluno_id: uuid.UUID, tenant_id: uuid.UUID) -> Aluno | None:
        stmt = (
            select(Aluno)
            .options(selectinload(Aluno.pessoa))
            .where(
                Aluno.id == aluno_id,
                Aluno.tenant_id == tenant_id,
                Aluno.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_aluno_detail(self, aluno_id: uuid.UUID, tenant_id: uuid.UUID) -> Aluno | None:
        stmt = (
            select(Aluno)
            .options(
                selectinload(Aluno.pessoa),
                selectinload(Aluno.vinculos).selectinload(
                    VinculoAlunoEncarregado.encarregado
                ).selectinload(Encarregado.pessoa),
            )
            .where(
                Aluno.id == aluno_id,
                Aluno.tenant_id == tenant_id,
                Aluno.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_alunos(
        self,
        tenant_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        nome: str | None = None,
        n_processo: str | None = None,
        status: str | None = None,
    ) -> tuple[list[Aluno], int]:
        base = (
            select(Aluno)
            .join(Aluno.pessoa)
            .where(Aluno.tenant_id == tenant_id, Aluno.deleted_at.is_(None))
        )
        if nome:
            base = base.where(Pessoa.nome_completo.ilike(f"%{nome}%"))
        if n_processo:
            base = base.where(Aluno.n_processo == n_processo)
        if status:
            base = base.where(Aluno.status == status)

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = (
            base.options(selectinload(Aluno.pessoa))
            .order_by(Pessoa.nome_completo)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_aluno_by_n_processo(
        self, tenant_id: uuid.UUID, n_processo: str
    ) -> Aluno | None:
        stmt = select(Aluno).where(
            Aluno.tenant_id == tenant_id,
            Aluno.n_processo == n_processo,
            Aluno.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_aluno(self, aluno: Aluno) -> Aluno:
        self.db.add(aluno)
        await self.db.flush()
        await self.db.refresh(aluno)
        return aluno

    # ── Professor ───────────────────────────────

    async def get_professor(self, professor_id: uuid.UUID, tenant_id: uuid.UUID) -> Professor | None:
        stmt = (
            select(Professor)
            .options(selectinload(Professor.pessoa))
            .where(
                Professor.id == professor_id,
                Professor.tenant_id == tenant_id,
                Professor.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_professores(
        self,
        tenant_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        especialidade: str | None = None,
        tipo_contrato: str | None = None,
    ) -> tuple[list[Professor], int]:
        base = (
            select(Professor)
            .join(Professor.pessoa)
            .where(Professor.tenant_id == tenant_id, Professor.deleted_at.is_(None))
        )
        if especialidade:
            base = base.where(Professor.especialidade.ilike(f"%{especialidade}%"))
        if tipo_contrato:
            base = base.where(Professor.tipo_contrato == tipo_contrato)

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = (
            base.options(selectinload(Professor.pessoa))
            .order_by(Pessoa.nome_completo)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def create_professor(self, professor: Professor) -> Professor:
        self.db.add(professor)
        await self.db.flush()
        await self.db.refresh(professor)
        return professor

    # ── Encarregado ─────────────────────────────

    async def get_encarregado(
        self, encarregado_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Encarregado | None:
        stmt = (
            select(Encarregado)
            .options(selectinload(Encarregado.pessoa))
            .where(
                Encarregado.id == encarregado_id,
                Encarregado.tenant_id == tenant_id,
                Encarregado.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_encarregados(
        self,
        tenant_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Encarregado], int]:
        base = (
            select(Encarregado)
            .join(Encarregado.pessoa)
            .where(Encarregado.tenant_id == tenant_id, Encarregado.deleted_at.is_(None))
        )

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = (
            base.options(selectinload(Encarregado.pessoa))
            .order_by(Pessoa.nome_completo)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def create_encarregado(self, encarregado: Encarregado) -> Encarregado:
        self.db.add(encarregado)
        await self.db.flush()
        await self.db.refresh(encarregado)
        return encarregado

    # ── Funcionário ─────────────────────────────

    async def create_funcionario(self, funcionario: Funcionario) -> Funcionario:
        self.db.add(funcionario)
        await self.db.flush()
        await self.db.refresh(funcionario)
        return funcionario

    # ── Vínculo Aluno ↔ Encarregado ─────────────

    async def get_vinculo(
        self, vinculo_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> VinculoAlunoEncarregado | None:
        stmt = select(VinculoAlunoEncarregado).where(
            VinculoAlunoEncarregado.id == vinculo_id,
            VinculoAlunoEncarregado.tenant_id == tenant_id,
            VinculoAlunoEncarregado.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_vinculo_existente(
        self, aluno_id: uuid.UUID, encarregado_id: uuid.UUID
    ) -> VinculoAlunoEncarregado | None:
        stmt = select(VinculoAlunoEncarregado).where(
            VinculoAlunoEncarregado.aluno_id == aluno_id,
            VinculoAlunoEncarregado.encarregado_id == encarregado_id,
            VinculoAlunoEncarregado.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_vinculos(
        self, aluno_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[VinculoAlunoEncarregado]:
        stmt = (
            select(VinculoAlunoEncarregado)
            .options(
                selectinload(VinculoAlunoEncarregado.encarregado).selectinload(
                    Encarregado.pessoa
                )
            )
            .where(
                VinculoAlunoEncarregado.aluno_id == aluno_id,
                VinculoAlunoEncarregado.tenant_id == tenant_id,
                VinculoAlunoEncarregado.deleted_at.is_(None),
            )
            .order_by(VinculoAlunoEncarregado.principal.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_vinculo(
        self, vinculo: VinculoAlunoEncarregado
    ) -> VinculoAlunoEncarregado:
        self.db.add(vinculo)
        await self.db.flush()
        await self.db.refresh(vinculo)
        return vinculo

    async def unset_principal(self, aluno_id: uuid.UUID, tenant_id: uuid.UUID) -> None:
        """Remove a flag principal de todos os vínculos do aluno."""
        stmt = select(VinculoAlunoEncarregado).where(
            VinculoAlunoEncarregado.aluno_id == aluno_id,
            VinculoAlunoEncarregado.tenant_id == tenant_id,
            VinculoAlunoEncarregado.principal.is_(True),
        )
        result = await self.db.execute(stmt)
        for v in result.scalars().all():
            v.principal = False