"""Repository for the academico module."""

import uuid
from datetime import time

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.modules.academico.infrastructure.models import (
    Curriculo,
    DiarioClasse,
    Disciplina,
    HorarioAula,
    PresencaDiario,
    Turma,
)


class AcademicoRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Currículo ───────────────────────────────

    async def get_curriculo(
        self, curriculo_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Curriculo | None:
        stmt = (
            select(Curriculo)
            .options(selectinload(Curriculo.disciplinas))
            .where(
                Curriculo.id == curriculo_id,
                Curriculo.tenant_id == tenant_id,
                Curriculo.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_curriculos(
        self,
        tenant_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Curriculo], int]:
        base = select(Curriculo).where(
            Curriculo.tenant_id == tenant_id, Curriculo.deleted_at.is_(None)
        )
        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = base.order_by(Curriculo.classe).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def create_curriculo(self, curriculo: Curriculo) -> Curriculo:
        self.db.add(curriculo)
        await self.db.flush()
        await self.db.refresh(curriculo)
        return curriculo

    # ── Disciplina ──────────────────────────────

    async def get_disciplina(
        self, disciplina_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Disciplina | None:
        stmt = select(Disciplina).where(
            Disciplina.id == disciplina_id,
            Disciplina.tenant_id == tenant_id,
            Disciplina.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_disciplina_by_codigo(
        self, tenant_id: uuid.UUID, codigo: str
    ) -> Disciplina | None:
        stmt = select(Disciplina).where(
            Disciplina.tenant_id == tenant_id,
            Disciplina.codigo == codigo,
            Disciplina.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_disciplinas(
        self,
        tenant_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        curriculo_id: uuid.UUID | None = None,
    ) -> tuple[list[Disciplina], int]:
        base = select(Disciplina).where(
            Disciplina.tenant_id == tenant_id, Disciplina.deleted_at.is_(None)
        )
        if curriculo_id:
            base = base.where(Disciplina.curriculo_id == curriculo_id)

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = base.order_by(Disciplina.nome).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def create_disciplina(self, disciplina: Disciplina) -> Disciplina:
        self.db.add(disciplina)
        await self.db.flush()
        await self.db.refresh(disciplina)
        return disciplina

    # ── Turma ───────────────────────────────────

    async def get_turma(
        self, turma_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Turma | None:
        stmt = (
            select(Turma)
            .options(selectinload(Turma.horarios))
            .where(
                Turma.id == turma_id,
                Turma.tenant_id == tenant_id,
                Turma.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_turmas(
        self,
        tenant_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        ano_letivo_id: uuid.UUID | None = None,
        classe: str | None = None,
        turno: str | None = None,
    ) -> tuple[list[Turma], int]:
        base = select(Turma).where(
            Turma.tenant_id == tenant_id, Turma.deleted_at.is_(None)
        )
        if ano_letivo_id:
            base = base.where(Turma.ano_letivo_id == ano_letivo_id)
        if classe:
            base = base.where(Turma.classe == classe)
        if turno:
            base = base.where(Turma.turno == turno)

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = base.order_by(Turma.nome).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def create_turma(self, turma: Turma) -> Turma:
        self.db.add(turma)
        await self.db.flush()
        await self.db.refresh(turma)
        return turma

    # ── Horário ─────────────────────────────────

    async def check_conflito_professor(
        self,
        tenant_id: uuid.UUID,
        professor_id: uuid.UUID,
        dia_semana: str,
        hora_inicio: time,
        hora_fim: time,
    ) -> HorarioAula | None:
        stmt = select(HorarioAula).where(
            HorarioAula.tenant_id == tenant_id,
            HorarioAula.professor_id == professor_id,
            HorarioAula.dia_semana == dia_semana,
            HorarioAula.hora_inicio < hora_fim,
            HorarioAula.hora_fim > hora_inicio,
            HorarioAula.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def check_conflito_turma(
        self,
        tenant_id: uuid.UUID,
        turma_id: uuid.UUID,
        dia_semana: str,
        hora_inicio: time,
        hora_fim: time,
    ) -> HorarioAula | None:
        stmt = select(HorarioAula).where(
            HorarioAula.tenant_id == tenant_id,
            HorarioAula.turma_id == turma_id,
            HorarioAula.dia_semana == dia_semana,
            HorarioAula.hora_inicio < hora_fim,
            HorarioAula.hora_fim > hora_inicio,
            HorarioAula.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_horarios_turma(
        self, turma_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[HorarioAula]:
        stmt = (
            select(HorarioAula)
            .where(
                HorarioAula.turma_id == turma_id,
                HorarioAula.tenant_id == tenant_id,
                HorarioAula.deleted_at.is_(None),
            )
            .order_by(HorarioAula.dia_semana, HorarioAula.hora_inicio)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_horarios_professor(
        self, professor_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[HorarioAula]:
        stmt = (
            select(HorarioAula)
            .where(
                HorarioAula.professor_id == professor_id,
                HorarioAula.tenant_id == tenant_id,
                HorarioAula.deleted_at.is_(None),
            )
            .order_by(HorarioAula.dia_semana, HorarioAula.hora_inicio)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_horario(self, horario: HorarioAula) -> HorarioAula:
        self.db.add(horario)
        await self.db.flush()
        await self.db.refresh(horario)
        return horario

    # ── Diário de Classe ────────────────────────

    async def get_diario(
        self, diario_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> DiarioClasse | None:
        stmt = (
            select(DiarioClasse)
            .options(selectinload(DiarioClasse.presencas))
            .where(
                DiarioClasse.id == diario_id,
                DiarioClasse.tenant_id == tenant_id,
                DiarioClasse.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_diarios(
        self,
        tenant_id: uuid.UUID,
        turma_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        disciplina_id: uuid.UUID | None = None,
    ) -> tuple[list[DiarioClasse], int]:
        base = select(DiarioClasse).where(
            DiarioClasse.tenant_id == tenant_id,
            DiarioClasse.turma_id == turma_id,
            DiarioClasse.deleted_at.is_(None),
        )
        if disciplina_id:
            base = base.where(DiarioClasse.disciplina_id == disciplina_id)

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = (
            base.options(selectinload(DiarioClasse.presencas))
            .order_by(DiarioClasse.data_aula.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def create_diario(self, diario: DiarioClasse) -> DiarioClasse:
        self.db.add(diario)
        await self.db.flush()
        await self.db.refresh(diario)
        return diario

    async def create_presenca(self, presenca: PresencaDiario) -> PresencaDiario:
        self.db.add(presenca)
        await self.db.flush()
        return presenca
