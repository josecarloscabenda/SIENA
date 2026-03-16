"""Application services for the avaliacoes module."""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.avaliacoes.infrastructure.models import Avaliacao, Falta, Nota
from src.modules.avaliacoes.infrastructure.repository import AvaliacoesRepository


class NotaService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = AvaliacoesRepository(db)

    async def create_avaliacao(
        self,
        tenant_id: uuid.UUID,
        turma_id: uuid.UUID,
        disciplina_id: uuid.UUID,
        tipo: str,
        periodo: int,
        data: date,
        peso: float,
        nota_maxima: int,
    ) -> Avaliacao:
        avaliacao = Avaliacao(
            tenant_id=tenant_id,
            turma_id=turma_id,
            disciplina_id=disciplina_id,
            tipo=tipo,
            periodo=periodo,
            data=data,
            peso=peso,
            nota_maxima=nota_maxima,
        )
        avaliacao = await self.repo.create_avaliacao(avaliacao)
        await self.db.commit()
        return await self.repo.get_avaliacao(avaliacao.id, tenant_id)  # type: ignore[return-value]

    async def list_avaliacoes(
        self,
        tenant_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        turma_id: uuid.UUID | None = None,
        disciplina_id: uuid.UUID | None = None,
        periodo: int | None = None,
    ) -> tuple[list[Avaliacao], int]:
        return await self.repo.list_avaliacoes(
            tenant_id, offset, limit, turma_id, disciplina_id, periodo
        )

    async def lancar_notas(
        self,
        tenant_id: uuid.UUID,
        avaliacao_id: uuid.UUID,
        professor_id: uuid.UUID,
        notas: list[dict],
    ) -> list[Nota]:
        avaliacao = await self.repo.get_avaliacao(avaliacao_id, tenant_id)
        if avaliacao is None:
            raise NotFoundError("Avaliação não encontrada")

        result = []
        for item in notas:
            valor = Decimal(str(item["valor"]))
            if valor < 0 or valor > avaliacao.nota_maxima:
                raise InvalidDataError(
                    f"Nota {valor} fora do intervalo [0, {avaliacao.nota_maxima}]"
                )

            existing = await self.repo.get_nota_existente(
                avaliacao_id, item["aluno_id"]
            )
            if existing:
                existing.valor = valor
                existing.observacoes = item.get("observacoes")
                existing.lancado_por = professor_id
                result.append(existing)
            else:
                nota = Nota(
                    tenant_id=tenant_id,
                    avaliacao_id=avaliacao_id,
                    aluno_id=item["aluno_id"],
                    valor=valor,
                    observacoes=item.get("observacoes"),
                    lancado_por=professor_id,
                )
                nota = await self.repo.create_nota(nota)
                result.append(nota)

        await self.db.commit()
        return result

    async def list_notas_avaliacao(
        self, avaliacao_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[Nota]:
        avaliacao = await self.repo.get_avaliacao(avaliacao_id, tenant_id)
        if avaliacao is None:
            raise NotFoundError("Avaliação não encontrada")
        return await self.repo.list_notas_avaliacao(avaliacao_id, tenant_id)

    async def update_nota(
        self,
        nota_id: uuid.UUID,
        tenant_id: uuid.UUID,
        valor: Decimal | None = None,
        observacoes: str | None = None,
    ) -> Nota:
        nota = await self.repo.get_nota(nota_id, tenant_id)
        if nota is None:
            raise NotFoundError("Nota não encontrada")

        if valor is not None:
            avaliacao = await self.repo.get_avaliacao(nota.avaliacao_id, tenant_id)
            if avaliacao and (valor < 0 or valor > avaliacao.nota_maxima):
                raise InvalidDataError(
                    f"Nota {valor} fora do intervalo [0, {avaliacao.nota_maxima}]"
                )
            nota.valor = valor

        if observacoes is not None:
            nota.observacoes = observacoes

        await self.db.commit()
        return nota

    async def list_notas_aluno(
        self, aluno_id: uuid.UUID, tenant_id: uuid.UUID, periodo: int | None = None
    ) -> list[Nota]:
        return await self.repo.list_notas_aluno(aluno_id, tenant_id, periodo)

    async def list_notas_turma(
        self, turma_id: uuid.UUID, tenant_id: uuid.UUID, periodo: int | None = None
    ) -> list[Nota]:
        return await self.repo.list_notas_turma(turma_id, tenant_id, periodo)


class FaltaService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = AvaliacoesRepository(db)

    async def lancar_faltas(
        self,
        tenant_id: uuid.UUID,
        turma_id: uuid.UUID,
        data: date,
        faltas: list[dict],
    ) -> list[Falta]:
        result = []
        for item in faltas:
            falta = Falta(
                tenant_id=tenant_id,
                aluno_id=item["aluno_id"],
                turma_id=turma_id,
                disciplina_id=item["disciplina_id"],
                data=data,
                tipo=item["tipo"],
                justificativa=item.get("justificativa"),
            )
            falta = await self.repo.create_falta(falta)
            result.append(falta)

        await self.db.commit()
        return result

    async def list_faltas_aluno(
        self,
        aluno_id: uuid.UUID,
        tenant_id: uuid.UUID,
        disciplina_id: uuid.UUID | None = None,
        tipo: str | None = None,
    ) -> list[Falta]:
        return await self.repo.list_faltas_aluno(
            aluno_id, tenant_id, disciplina_id, tipo
        )

    async def resumo_faltas(
        self, aluno_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> dict:
        return await self.repo.count_faltas_aluno(aluno_id, tenant_id)


class BoletimService:
    """Gera boletim JSON (PDF fica para a Fase 2)."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = AvaliacoesRepository(db)

    async def gerar_boletim(
        self,
        aluno_id: uuid.UUID,
        tenant_id: uuid.UUID,
        periodo: int,
    ) -> dict:
        notas = await self.repo.list_notas_aluno(aluno_id, tenant_id, periodo)
        faltas = await self.repo.list_faltas_aluno(aluno_id, tenant_id)

        # Agrupar notas por disciplina
        disc_notas: dict[uuid.UUID, list[Nota]] = {}
        for n in notas:
            disc_notas.setdefault(n.avaliacao.disciplina_id, []).append(n)

        # Agrupar faltas por disciplina
        disc_faltas: dict[uuid.UUID, int] = {}
        for f in faltas:
            disc_faltas[f.disciplina_id] = disc_faltas.get(f.disciplina_id, 0) + 1

        disciplinas = []
        all_disc_ids = set(disc_notas.keys()) | set(disc_faltas.keys())
        for disc_id in all_disc_ids:
            notas_disc = disc_notas.get(disc_id, [])
            if notas_disc:
                total_peso = sum(n.avaliacao.peso for n in notas_disc)
                if total_peso > 0:
                    media = sum(
                        n.valor * Decimal(str(n.avaliacao.peso)) for n in notas_disc
                    ) / Decimal(str(total_peso))
                else:
                    media = None
            else:
                media = None

            disciplinas.append({
                "disciplina_id": str(disc_id),
                "disciplina_nome": "",  # Would need join for name
                "media": float(media) if media is not None else None,
                "faltas_total": disc_faltas.get(disc_id, 0),
            })

        return {
            "aluno_id": str(aluno_id),
            "periodo": periodo,
            "disciplinas": disciplinas,
        }


# ── Domain Errors ───────────────────────────────

class AvaliacoesError(Exception):
    pass


class NotFoundError(AvaliacoesError):
    pass


class InvalidDataError(AvaliacoesError):
    pass
