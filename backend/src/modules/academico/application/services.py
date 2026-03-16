"""Application services for the academico module."""

import uuid
from datetime import time

from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.academico.infrastructure.models import (
    Curriculo,
    DiarioClasse,
    Disciplina,
    HorarioAula,
    PresencaDiario,
    Turma,
)
from src.modules.academico.infrastructure.repository import AcademicoRepository


class CurriculoService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = AcademicoRepository(db)

    async def create_curriculo(
        self,
        tenant_id: uuid.UUID,
        nivel: str,
        classe: str,
        ano_letivo_id: uuid.UUID,
        carga_horaria_total: int,
    ) -> Curriculo:
        curriculo = Curriculo(
            tenant_id=tenant_id,
            nivel=nivel,
            classe=classe,
            ano_letivo_id=ano_letivo_id,
            carga_horaria_total=carga_horaria_total,
        )
        curriculo = await self.repo.create_curriculo(curriculo)
        await self.db.commit()
        return await self.repo.get_curriculo(curriculo.id, tenant_id)  # type: ignore[return-value]

    async def get_curriculo(
        self, curriculo_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Curriculo | None:
        return await self.repo.get_curriculo(curriculo_id, tenant_id)

    async def list_curriculos(
        self, tenant_id: uuid.UUID, offset: int = 0, limit: int = 20
    ) -> tuple[list[Curriculo], int]:
        return await self.repo.list_curriculos(tenant_id, offset, limit)


class DisciplinaService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = AcademicoRepository(db)

    async def create_disciplina(
        self,
        tenant_id: uuid.UUID,
        nome: str,
        codigo: str,
        curriculo_id: uuid.UUID,
        carga_horaria_semanal: int,
    ) -> Disciplina:
        existing = await self.repo.get_disciplina_by_codigo(tenant_id, codigo)
        if existing:
            raise DuplicateCodigoError(codigo)

        curriculo = await self.repo.get_curriculo(curriculo_id, tenant_id)
        if curriculo is None:
            raise NotFoundError("Currículo não encontrado")

        disciplina = Disciplina(
            tenant_id=tenant_id,
            nome=nome,
            codigo=codigo,
            curriculo_id=curriculo_id,
            carga_horaria_semanal=carga_horaria_semanal,
        )
        disciplina = await self.repo.create_disciplina(disciplina)
        await self.db.commit()
        return disciplina

    async def list_disciplinas(
        self,
        tenant_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        curriculo_id: uuid.UUID | None = None,
    ) -> tuple[list[Disciplina], int]:
        return await self.repo.list_disciplinas(tenant_id, offset, limit, curriculo_id)


class TurmaService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = AcademicoRepository(db)

    async def create_turma(
        self,
        tenant_id: uuid.UUID,
        nome: str,
        classe: str,
        turno: str,
        ano_letivo_id: uuid.UUID,
        capacidade_max: int,
        professor_regente_id: uuid.UUID,
        sala: str | None = None,
    ) -> Turma:
        turma = Turma(
            tenant_id=tenant_id,
            nome=nome,
            classe=classe,
            turno=turno,
            ano_letivo_id=ano_letivo_id,
            capacidade_max=capacidade_max,
            professor_regente_id=professor_regente_id,
            sala=sala,
        )
        turma = await self.repo.create_turma(turma)
        await self.db.commit()
        return await self.repo.get_turma(turma.id, tenant_id)  # type: ignore[return-value]

    async def get_turma(
        self, turma_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Turma | None:
        return await self.repo.get_turma(turma_id, tenant_id)

    async def list_turmas(
        self,
        tenant_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        ano_letivo_id: uuid.UUID | None = None,
        classe: str | None = None,
        turno: str | None = None,
    ) -> tuple[list[Turma], int]:
        return await self.repo.list_turmas(
            tenant_id, offset, limit, ano_letivo_id, classe, turno
        )


class HorarioService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = AcademicoRepository(db)

    async def create_horario(
        self,
        tenant_id: uuid.UUID,
        turma_id: uuid.UUID,
        disciplina_id: uuid.UUID,
        professor_id: uuid.UUID,
        dia_semana: str,
        hora_inicio: time,
        hora_fim: time,
    ) -> HorarioAula:
        # Validar turma
        turma = await self.repo.get_turma(turma_id, tenant_id)
        if turma is None:
            raise NotFoundError("Turma não encontrada")

        if hora_fim <= hora_inicio:
            raise InvalidDataError("Hora de fim deve ser posterior à hora de início")

        # Verificar conflito do professor
        conflito_prof = await self.repo.check_conflito_professor(
            tenant_id, professor_id, dia_semana, hora_inicio, hora_fim
        )
        if conflito_prof:
            raise ConflictError("Professor já tem aula neste horário")

        # Verificar conflito da turma
        conflito_turma = await self.repo.check_conflito_turma(
            tenant_id, turma_id, dia_semana, hora_inicio, hora_fim
        )
        if conflito_turma:
            raise ConflictError("Turma já tem aula neste horário")

        horario = HorarioAula(
            tenant_id=tenant_id,
            turma_id=turma_id,
            disciplina_id=disciplina_id,
            professor_id=professor_id,
            dia_semana=dia_semana,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
        )
        horario = await self.repo.create_horario(horario)
        await self.db.commit()
        return horario

    async def list_horarios_turma(
        self, turma_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[HorarioAula]:
        turma = await self.repo.get_turma(turma_id, tenant_id)
        if turma is None:
            raise NotFoundError("Turma não encontrada")
        return await self.repo.list_horarios_turma(turma_id, tenant_id)

    async def list_horarios_professor(
        self, professor_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[HorarioAula]:
        return await self.repo.list_horarios_professor(professor_id, tenant_id)


class DiarioService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = AcademicoRepository(db)

    async def registar_aula(
        self,
        tenant_id: uuid.UUID,
        professor_id: uuid.UUID,
        turma_id: uuid.UUID,
        disciplina_id: uuid.UUID,
        data_aula: object,
        conteudo: str,
        sumario: str,
        observacoes: str | None = None,
        presencas: list[dict] | None = None,
    ) -> DiarioClasse:
        turma = await self.repo.get_turma(turma_id, tenant_id)
        if turma is None:
            raise NotFoundError("Turma não encontrada")

        diario = DiarioClasse(
            tenant_id=tenant_id,
            turma_id=turma_id,
            disciplina_id=disciplina_id,
            professor_id=professor_id,
            data_aula=data_aula,
            conteudo=conteudo,
            sumario=sumario,
            observacoes=observacoes,
        )
        diario = await self.repo.create_diario(diario)

        # Registar presenças
        if presencas:
            for p in presencas:
                presenca = PresencaDiario(
                    tenant_id=tenant_id,
                    diario_id=diario.id,
                    aluno_id=p["aluno_id"],
                    presente=p["presente"],
                    justificativa=p.get("justificativa"),
                )
                await self.repo.create_presenca(presenca)

        await self.db.commit()
        return await self.repo.get_diario(diario.id, tenant_id)  # type: ignore[return-value]

    async def list_diarios(
        self,
        tenant_id: uuid.UUID,
        turma_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        disciplina_id: uuid.UUID | None = None,
    ) -> tuple[list[DiarioClasse], int]:
        return await self.repo.list_diarios(
            tenant_id, turma_id, offset, limit, disciplina_id
        )


# ── Domain Errors ───────────────────────────────

class AcademicoError(Exception):
    pass


class NotFoundError(AcademicoError):
    pass


class ConflictError(AcademicoError):
    pass


class DuplicateCodigoError(AcademicoError):
    def __init__(self, codigo: str) -> None:
        super().__init__(f"Código de disciplina '{codigo}' já existe neste tenant")


class InvalidDataError(AcademicoError):
    pass
