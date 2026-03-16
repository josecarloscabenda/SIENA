"""Service for importing historical notas from CSV."""

import csv
import uuid
from decimal import Decimal, InvalidOperation
from io import StringIO

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.avaliacoes.infrastructure.models import Avaliacao, Nota
from src.modules.directory.infrastructure.models import Aluno


class ImportResult:
    """Tracks the outcome of a CSV import operation."""

    def __init__(self) -> None:
        self.created = 0
        self.skipped = 0
        self.errors: list[dict] = []  # [{row: int, field: str, message: str}]

    def to_dict(self) -> dict:
        return {
            "created": self.created,
            "skipped": self.skipped,
            "errors": self.errors,
            "total_processed": self.created + self.skipped + len(self.errors),
        }


async def import_notas_csv(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    professor_id: uuid.UUID,
    csv_content: str,
) -> ImportResult:
    """Import notas from CSV content.

    Expected columns:
        n_processo, avaliacao_id (UUID), valor (numeric),
        observacoes (optional)

    Matches alunos by n_processo within the tenant.
    If a nota already exists for the same (avaliacao, aluno), it is updated
    (counted as "skipped" in the report).
    """
    result = ImportResult()
    reader = csv.DictReader(StringIO(csv_content))

    required_fields = ["n_processo", "avaliacao_id", "valor"]

    for row_num, row in enumerate(reader, start=2):  # row 1 is header
        # ── Validate required fields ────────────────────────────
        missing = [f for f in required_fields if not row.get(f, "").strip()]
        if missing:
            result.errors.append({
                "row": row_num,
                "field": ", ".join(missing),
                "message": f"Campos obrigatórios em falta: {', '.join(missing)}",
            })
            continue

        # ── Find aluno by n_processo ────────────────────────────
        n_processo = row["n_processo"].strip()
        aluno_result = await session.execute(
            select(Aluno).where(
                Aluno.tenant_id == tenant_id,
                Aluno.n_processo == n_processo,
                Aluno.deleted_at.is_(None),
            )
        )
        aluno = aluno_result.scalar_one_or_none()
        if not aluno:
            result.errors.append({
                "row": row_num,
                "field": "n_processo",
                "message": f"Aluno não encontrado: {n_processo}",
            })
            continue

        # ── Validate avaliacao_id ───────────────────────────────
        try:
            avaliacao_id = uuid.UUID(row["avaliacao_id"].strip())
        except ValueError:
            result.errors.append({
                "row": row_num,
                "field": "avaliacao_id",
                "message": f"UUID inválido: {row['avaliacao_id']}",
            })
            continue

        # ── Check avaliacao exists ──────────────────────────────
        av_result = await session.execute(
            select(Avaliacao).where(
                Avaliacao.id == avaliacao_id,
                Avaliacao.tenant_id == tenant_id,
            )
        )
        avaliacao = av_result.scalar_one_or_none()
        if not avaliacao:
            result.errors.append({
                "row": row_num,
                "field": "avaliacao_id",
                "message": f"Avaliação não encontrada: {row['avaliacao_id']}",
            })
            continue

        # ── Validate valor ──────────────────────────────────────
        try:
            valor = Decimal(row["valor"].strip())
        except InvalidOperation:
            result.errors.append({
                "row": row_num,
                "field": "valor",
                "message": f"Valor inválido: {row['valor']}",
            })
            continue

        if valor < 0 or valor > avaliacao.nota_maxima:
            result.errors.append({
                "row": row_num,
                "field": "valor",
                "message": f"Valor fora do intervalo [0, {avaliacao.nota_maxima}]",
            })
            continue

        # ── Upsert nota ────────────────────────────────────────
        observacoes = row.get("observacoes", "").strip() or None

        existing_nota_result = await session.execute(
            select(Nota).where(
                Nota.avaliacao_id == avaliacao_id,
                Nota.aluno_id == aluno.id,
            )
        )
        nota = existing_nota_result.scalar_one_or_none()

        if nota:
            nota.valor = valor
            nota.observacoes = observacoes
            result.skipped += 1  # updated, counted as skipped
        else:
            nota = Nota(
                tenant_id=tenant_id,
                avaliacao_id=avaliacao_id,
                aluno_id=aluno.id,
                valor=valor,
                observacoes=observacoes,
                lancado_por=professor_id,
            )
            session.add(nota)
            result.created += 1

    await session.commit()
    return result
