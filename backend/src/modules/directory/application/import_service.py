"""Service for importing directory data from CSV."""

import csv
import uuid
from datetime import date
from io import StringIO

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.directory.infrastructure.models import Aluno, Pessoa


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


async def import_alunos_csv(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    csv_content: str,
) -> ImportResult:
    """Import alunos from CSV content.

    Expected columns:
        nome_completo, bi_identificacao, dt_nascimento (YYYY-MM-DD),
        sexo (M/F), n_processo, ano_ingresso,
        nacionalidade (optional), telefone (optional), email (optional)

    Rows with duplicate BI or n_processo (within the tenant) are skipped.
    """
    result = ImportResult()
    reader = csv.DictReader(StringIO(csv_content))

    required_fields = [
        "nome_completo",
        "bi_identificacao",
        "dt_nascimento",
        "sexo",
        "n_processo",
        "ano_ingresso",
    ]

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

        # ── Check for duplicate BI ──────────────────────────────
        bi = row["bi_identificacao"].strip()
        existing_pessoa = await session.execute(
            select(Pessoa).where(
                Pessoa.tenant_id == tenant_id,
                Pessoa.bi_identificacao == bi,
                Pessoa.deleted_at.is_(None),
            )
        )
        if existing_pessoa.scalar_one_or_none():
            result.skipped += 1
            continue

        # ── Validate dt_nascimento ──────────────────────────────
        try:
            dt_nasc = date.fromisoformat(row["dt_nascimento"].strip())
        except ValueError:
            result.errors.append({
                "row": row_num,
                "field": "dt_nascimento",
                "message": f"Data inválida: {row['dt_nascimento']}. Use formato YYYY-MM-DD.",
            })
            continue

        # ── Validate sexo ───────────────────────────────────────
        sexo = row["sexo"].strip().upper()
        if sexo not in ("M", "F"):
            result.errors.append({
                "row": row_num,
                "field": "sexo",
                "message": f"Sexo inválido: {row['sexo']}. Use M ou F.",
            })
            continue

        # ── Validate ano_ingresso ───────────────────────────────
        try:
            ano_ingresso = int(row["ano_ingresso"].strip())
        except ValueError:
            result.errors.append({
                "row": row_num,
                "field": "ano_ingresso",
                "message": f"Ano inválido: {row['ano_ingresso']}",
            })
            continue

        # ── Check duplicate n_processo ──────────────────────────
        n_processo = row["n_processo"].strip()
        existing_aluno = await session.execute(
            select(Aluno).where(
                Aluno.tenant_id == tenant_id,
                Aluno.n_processo == n_processo,
                Aluno.deleted_at.is_(None),
            )
        )
        if existing_aluno.scalar_one_or_none():
            result.skipped += 1
            continue

        # ── Create Pessoa + Aluno ───────────────────────────────
        pessoa = Pessoa(
            tenant_id=tenant_id,
            nome_completo=row["nome_completo"].strip(),
            bi_identificacao=bi,
            dt_nascimento=dt_nasc,
            sexo=sexo,
            nacionalidade=row.get("nacionalidade", "").strip() or "Angolana",
            telefone=row.get("telefone", "").strip() or None,
            email=row.get("email", "").strip() or None,
        )
        session.add(pessoa)
        await session.flush()

        aluno = Aluno(
            tenant_id=tenant_id,
            pessoa_id=pessoa.id,
            n_processo=n_processo,
            ano_ingresso=ano_ingresso,
        )
        session.add(aluno)
        result.created += 1

    await session.commit()
    return result
