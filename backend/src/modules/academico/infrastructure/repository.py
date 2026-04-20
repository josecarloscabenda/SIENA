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
from src.modules.directory.infrastructure.models import Pessoa, Professor
from src.modules.escolas.infrastructure.models import AnoLetivo


def _attach(obj, **kwargs):
    """Attach display fields to a SQLAlchemy object for DTO serialization."""
    for k, v in kwargs.items():
        setattr(obj, k, v)
    return obj


class AcademicoRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Currículo ───────────────────────────────

    async def get_curriculo(
        self, curriculo_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Curriculo | None:
        stmt = (
            select(Curriculo, AnoLetivo.designacao.label("ano_letivo_designacao"))
            .options(selectinload(Curriculo.disciplinas))
            .outerjoin(AnoLetivo, AnoLetivo.id == Curriculo.ano_letivo_id)
            .where(
                Curriculo.id == curriculo_id,
                Curriculo.tenant_id == tenant_id,
                Curriculo.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        row = result.first()
        if row is None:
            return None
        curriculo = _attach(row.Curriculo, ano_letivo_designacao=row.ano_letivo_designacao)
        for d in curriculo.disciplinas:
            d.curriculo_nome = f"{curriculo.nivel} — {curriculo.classe}"  # type: ignore[attr-defined]
        return curriculo

    async def list_curriculos(
        self,
        tenant_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Curriculo], int]:
        filters = [Curriculo.tenant_id == tenant_id, Curriculo.deleted_at.is_(None)]
        count_stmt = select(func.count(Curriculo.id)).where(*filters)
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = (
            select(Curriculo, AnoLetivo.designacao.label("ano_letivo_designacao"))
            .outerjoin(AnoLetivo, AnoLetivo.id == Curriculo.ano_letivo_id)
            .where(*filters)
            .order_by(Curriculo.classe)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        items = [
            _attach(row.Curriculo, ano_letivo_designacao=row.ano_letivo_designacao)
            for row in result.all()
        ]
        return items, total

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
        filters = [Disciplina.tenant_id == tenant_id, Disciplina.deleted_at.is_(None)]
        if curriculo_id:
            filters.append(Disciplina.curriculo_id == curriculo_id)

        count_stmt = select(func.count(Disciplina.id)).where(*filters)
        total = (await self.db.execute(count_stmt)).scalar_one()

        curriculo_label = (Curriculo.nivel + " — " + Curriculo.classe).label("curriculo_nome")
        stmt = (
            select(Disciplina, curriculo_label)
            .outerjoin(Curriculo, Curriculo.id == Disciplina.curriculo_id)
            .where(*filters)
            .order_by(Disciplina.nome)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        items = [
            _attach(row.Disciplina, curriculo_nome=row.curriculo_nome) for row in result.all()
        ]
        return items, total

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
            select(
                Turma,
                Pessoa.nome_completo.label("professor_regente_nome"),
                AnoLetivo.designacao.label("ano_letivo_designacao"),
            )
            .options(selectinload(Turma.horarios))
            .outerjoin(Professor, Professor.id == Turma.professor_regente_id)
            .outerjoin(Pessoa, Pessoa.id == Professor.pessoa_id)
            .outerjoin(AnoLetivo, AnoLetivo.id == Turma.ano_letivo_id)
            .where(
                Turma.id == turma_id,
                Turma.tenant_id == tenant_id,
                Turma.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        row = result.first()
        if row is None:
            return None
        turma = _attach(
            row.Turma,
            professor_regente_nome=row.professor_regente_nome,
            ano_letivo_designacao=row.ano_letivo_designacao,
        )
        if turma.horarios:
            await self._enrich_horarios(turma.horarios)
        return turma

    async def list_turmas(
        self,
        tenant_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        ano_letivo_id: uuid.UUID | None = None,
        classe: str | None = None,
        turno: str | None = None,
    ) -> tuple[list[Turma], int]:
        filters = [Turma.tenant_id == tenant_id, Turma.deleted_at.is_(None)]
        if ano_letivo_id:
            filters.append(Turma.ano_letivo_id == ano_letivo_id)
        if classe:
            filters.append(Turma.classe == classe)
        if turno:
            filters.append(Turma.turno == turno)

        count_stmt = select(func.count(Turma.id)).where(*filters)
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = (
            select(
                Turma,
                Pessoa.nome_completo.label("professor_regente_nome"),
                AnoLetivo.designacao.label("ano_letivo_designacao"),
            )
            .outerjoin(Professor, Professor.id == Turma.professor_regente_id)
            .outerjoin(Pessoa, Pessoa.id == Professor.pessoa_id)
            .outerjoin(AnoLetivo, AnoLetivo.id == Turma.ano_letivo_id)
            .where(*filters)
            .order_by(Turma.nome)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        items = [
            _attach(
                row.Turma,
                professor_regente_nome=row.professor_regente_nome,
                ano_letivo_designacao=row.ano_letivo_designacao,
            )
            for row in result.all()
        ]
        return items, total

    async def _enrich_horarios(self, horarios: list[HorarioAula]) -> None:
        """Populate disciplina_nome and professor_nome on horarios in-place."""
        if not horarios:
            return
        disciplina_ids = {h.disciplina_id for h in horarios}
        professor_ids = {h.professor_id for h in horarios}

        disc_map: dict[uuid.UUID, str] = {}
        if disciplina_ids:
            res = await self.db.execute(
                select(Disciplina.id, Disciplina.nome).where(Disciplina.id.in_(disciplina_ids))
            )
            disc_map = {r.id: r.nome for r in res.all()}

        prof_map: dict[uuid.UUID, str] = {}
        if professor_ids:
            res = await self.db.execute(
                select(Professor.id, Pessoa.nome_completo)
                .join(Pessoa, Pessoa.id == Professor.pessoa_id)
                .where(Professor.id.in_(professor_ids))
            )
            prof_map = {r.id: r.nome_completo for r in res.all()}

        for h in horarios:
            h.disciplina_nome = disc_map.get(h.disciplina_id)  # type: ignore[attr-defined]
            h.professor_nome = prof_map.get(h.professor_id)  # type: ignore[attr-defined]

    async def create_turma(self, turma: Turma) -> Turma:
        self.db.add(turma)
        await self.db.flush()
        await self.db.refresh(turma)
        # Populate display fields for response
        prof_res = await self.db.execute(
            select(Pessoa.nome_completo)
            .join(Professor, Professor.pessoa_id == Pessoa.id)
            .where(Professor.id == turma.professor_regente_id)
        )
        ano_res = await self.db.execute(
            select(AnoLetivo.designacao).where(AnoLetivo.id == turma.ano_letivo_id)
        )
        turma.professor_regente_nome = prof_res.scalar_one_or_none()  # type: ignore[attr-defined]
        turma.ano_letivo_designacao = ano_res.scalar_one_or_none()  # type: ignore[attr-defined]
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
        horarios = list(result.scalars().all())
        await self._enrich_horarios(horarios)
        return horarios

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
        horarios = list(result.scalars().all())
        await self._enrich_horarios(horarios)
        return horarios

    async def create_horario(self, horario: HorarioAula) -> HorarioAula:
        self.db.add(horario)
        await self.db.flush()
        await self.db.refresh(horario)
        await self._enrich_horarios([horario])
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
