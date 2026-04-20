"""Repository for the enrollment module."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.modules.directory.infrastructure.models import Aluno, Pessoa
from src.modules.enrollment.infrastructure.models import (
    AlocacaoTurma,
    DocumentoMatricula,
    Matricula,
    Transferencia,
)
from src.modules.escolas.infrastructure.models import AnoLetivo


def _enrich_matricula(
    m: Matricula, aluno_nome: str | None, aluno_n_processo: str | None, ano_letivo_designacao: str | None
) -> Matricula:
    """Attach display fields to a Matricula for DTO serialization."""
    m.aluno_nome = aluno_nome  # type: ignore[attr-defined]
    m.aluno_n_processo = aluno_n_processo  # type: ignore[attr-defined]
    m.ano_letivo_designacao = ano_letivo_designacao  # type: ignore[attr-defined]
    return m


class EnrollmentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Matrícula ───────────────────────────────

    async def get_matricula(
        self, matricula_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Matricula | None:
        stmt = (
            select(
                Matricula,
                Pessoa.nome_completo.label("aluno_nome"),
                Aluno.n_processo.label("aluno_n_processo"),
                AnoLetivo.designacao.label("ano_letivo_designacao"),
            )
            .options(
                selectinload(Matricula.alocacao),
                selectinload(Matricula.documentos),
            )
            .outerjoin(Aluno, Aluno.id == Matricula.aluno_id)
            .outerjoin(Pessoa, Pessoa.id == Aluno.pessoa_id)
            .outerjoin(AnoLetivo, AnoLetivo.id == Matricula.ano_letivo_id)
            .where(
                Matricula.id == matricula_id,
                Matricula.tenant_id == tenant_id,
                Matricula.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        row = result.first()
        if row is None:
            return None
        return _enrich_matricula(
            row.Matricula, row.aluno_nome, row.aluno_n_processo, row.ano_letivo_designacao
        )

    async def get_matricula_existente(
        self, tenant_id: uuid.UUID, aluno_id: uuid.UUID, ano_letivo_id: uuid.UUID
    ) -> Matricula | None:
        stmt = select(Matricula).where(
            Matricula.tenant_id == tenant_id,
            Matricula.aluno_id == aluno_id,
            Matricula.ano_letivo_id == ano_letivo_id,
            Matricula.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_matriculas(
        self,
        tenant_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        ano_letivo_id: uuid.UUID | None = None,
        classe: str | None = None,
        estado: str | None = None,
        turno: str | None = None,
    ) -> tuple[list[Matricula], int]:
        filters = [
            Matricula.tenant_id == tenant_id,
            Matricula.deleted_at.is_(None),
        ]
        if ano_letivo_id:
            filters.append(Matricula.ano_letivo_id == ano_letivo_id)
        if classe:
            filters.append(Matricula.classe == classe)
        if estado:
            filters.append(Matricula.estado == estado)
        if turno:
            filters.append(Matricula.turno == turno)

        count_stmt = select(func.count(Matricula.id)).where(*filters)
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = (
            select(
                Matricula,
                Pessoa.nome_completo.label("aluno_nome"),
                Aluno.n_processo.label("aluno_n_processo"),
                AnoLetivo.designacao.label("ano_letivo_designacao"),
            )
            .outerjoin(Aluno, Aluno.id == Matricula.aluno_id)
            .outerjoin(Pessoa, Pessoa.id == Aluno.pessoa_id)
            .outerjoin(AnoLetivo, AnoLetivo.id == Matricula.ano_letivo_id)
            .where(*filters)
            .order_by(Matricula.data_pedido.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        items = [
            _enrich_matricula(
                row.Matricula,
                row.aluno_nome,
                row.aluno_n_processo,
                row.ano_letivo_designacao,
            )
            for row in result.all()
        ]
        return items, total

    async def create_matricula(self, matricula: Matricula) -> Matricula:
        self.db.add(matricula)
        await self.db.flush()
        await self.db.refresh(matricula)
        return matricula

    # ── Alocação ────────────────────────────────

    async def get_alocacao_by_matricula(
        self, matricula_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> AlocacaoTurma | None:
        stmt = select(AlocacaoTurma).where(
            AlocacaoTurma.matricula_id == matricula_id,
            AlocacaoTurma.tenant_id == tenant_id,
            AlocacaoTurma.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def count_alocacoes_turma(
        self, turma_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> int:
        stmt = select(func.count()).where(
            AlocacaoTurma.turma_id == turma_id,
            AlocacaoTurma.tenant_id == tenant_id,
            AlocacaoTurma.deleted_at.is_(None),
        )
        return (await self.db.execute(stmt)).scalar_one()

    async def create_alocacao(self, alocacao: AlocacaoTurma) -> AlocacaoTurma:
        self.db.add(alocacao)
        await self.db.flush()
        await self.db.refresh(alocacao)
        return alocacao

    # ── Transferência ───────────────────────────

    async def get_transferencia(
        self, transferencia_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Transferencia | None:
        stmt = select(Transferencia).where(
            Transferencia.id == transferencia_id,
            Transferencia.tenant_id == tenant_id,
            Transferencia.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_transferencia(self, transferencia: Transferencia) -> Transferencia:
        self.db.add(transferencia)
        await self.db.flush()
        await self.db.refresh(transferencia)
        return transferencia

    # ── Documentos ──────────────────────────────

    async def list_documentos(
        self, matricula_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[DocumentoMatricula]:
        stmt = (
            select(DocumentoMatricula)
            .where(
                DocumentoMatricula.matricula_id == matricula_id,
                DocumentoMatricula.tenant_id == tenant_id,
                DocumentoMatricula.deleted_at.is_(None),
            )
            .order_by(DocumentoMatricula.uploaded_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_documento(self, doc: DocumentoMatricula) -> DocumentoMatricula:
        self.db.add(doc)
        await self.db.flush()
        await self.db.refresh(doc)
        return doc