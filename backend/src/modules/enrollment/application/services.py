"""Application services for the enrollment module."""

import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.enrollment.infrastructure.models import (
    AlocacaoTurma,
    DocumentoMatricula,
    Matricula,
    Transferencia,
)
from src.modules.enrollment.infrastructure.repository import EnrollmentRepository


class MatriculaService:
    """Serviço para gestão de matrículas."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = EnrollmentRepository(db)

    async def create_matricula(
        self,
        tenant_id: uuid.UUID,
        aluno_id: uuid.UUID,
        ano_letivo_id: uuid.UUID,
        classe: str,
        turno: str = "matutino",
        observacoes: str | None = None,
    ) -> Matricula:
        # Validar duplicado: aluno não pode ter 2 matrículas no mesmo ano
        existing = await self.repo.get_matricula_existente(
            tenant_id, aluno_id, ano_letivo_id
        )
        if existing:
            raise DuplicateMatriculaError()

        matricula = Matricula(
            tenant_id=tenant_id,
            aluno_id=aluno_id,
            ano_letivo_id=ano_letivo_id,
            classe=classe,
            turno=turno,
            estado="pendente",
            data_pedido=date.today(),
            observacoes=observacoes,
        )
        matricula = await self.repo.create_matricula(matricula)
        await self.db.commit()
        return await self.repo.get_matricula(matricula.id, tenant_id)  # type: ignore[return-value]

    async def get_matricula(
        self, matricula_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Matricula | None:
        return await self.repo.get_matricula(matricula_id, tenant_id)

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
        return await self.repo.list_matriculas(
            tenant_id, offset, limit, ano_letivo_id, classe, estado, turno
        )

    async def aprovar_matricula(
        self, matricula_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Matricula:
        matricula = await self.repo.get_matricula(matricula_id, tenant_id)
        if matricula is None:
            raise NotFoundError("Matrícula não encontrada")
        if matricula.estado != "pendente":
            raise InvalidStateError(
                f"Matrícula não pode ser aprovada — estado actual: {matricula.estado}"
            )

        matricula.estado = "aprovada"
        matricula.data_aprovacao = date.today()
        await self.db.commit()
        return await self.repo.get_matricula(matricula_id, tenant_id)  # type: ignore[return-value]

    async def rejeitar_matricula(
        self, matricula_id: uuid.UUID, tenant_id: uuid.UUID, motivo: str
    ) -> Matricula:
        matricula = await self.repo.get_matricula(matricula_id, tenant_id)
        if matricula is None:
            raise NotFoundError("Matrícula não encontrada")
        if matricula.estado != "pendente":
            raise InvalidStateError(
                f"Matrícula não pode ser rejeitada — estado actual: {matricula.estado}"
            )

        matricula.estado = "rejeitada"
        matricula.observacoes = motivo
        await self.db.commit()
        return await self.repo.get_matricula(matricula_id, tenant_id)  # type: ignore[return-value]


class AlocacaoService:
    """Serviço para alocação de alunos em turmas."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = EnrollmentRepository(db)

    async def alocar_em_turma(
        self,
        tenant_id: uuid.UUID,
        matricula_id: uuid.UUID,
        turma_id: uuid.UUID,
    ) -> AlocacaoTurma:
        # Validar matrícula existe e está aprovada
        matricula = await self.repo.get_matricula(matricula_id, tenant_id)
        if matricula is None:
            raise NotFoundError("Matrícula não encontrada")
        if matricula.estado != "aprovada":
            raise InvalidStateError(
                "Apenas matrículas aprovadas podem ser alocadas a uma turma"
            )

        # Validar se já tem alocação
        existing = await self.repo.get_alocacao_by_matricula(matricula_id, tenant_id)
        if existing:
            raise DuplicateAlocacaoError()

        alocacao = AlocacaoTurma(
            tenant_id=tenant_id,
            matricula_id=matricula_id,
            turma_id=turma_id,
            data_alocacao=date.today(),
        )
        alocacao = await self.repo.create_alocacao(alocacao)
        await self.db.commit()
        return alocacao


class TransferenciaService:
    """Serviço para transferências entre escolas."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = EnrollmentRepository(db)

    async def create_transferencia(
        self,
        tenant_id: uuid.UUID,
        aluno_id: uuid.UUID,
        escola_origem_id: uuid.UUID,
        escola_destino_id: uuid.UUID,
        motivo: str,
    ) -> Transferencia:
        transferencia = Transferencia(
            tenant_id=tenant_id,
            aluno_id=aluno_id,
            escola_origem_id=escola_origem_id,
            escola_destino_id=escola_destino_id,
            data_pedido=date.today(),
            estado="pendente",
            motivo=motivo,
        )
        transferencia = await self.repo.create_transferencia(transferencia)
        await self.db.commit()
        return transferencia

    async def aprovar_transferencia(
        self, transferencia_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Transferencia:
        transferencia = await self.repo.get_transferencia(transferencia_id, tenant_id)
        if transferencia is None:
            raise NotFoundError("Transferência não encontrada")
        if transferencia.estado != "pendente":
            raise InvalidStateError(
                f"Transferência não pode ser aprovada — estado actual: {transferencia.estado}"
            )

        transferencia.estado = "aprovada"
        await self.db.commit()
        return transferencia


class DocumentoService:
    """Serviço para documentos de matrícula."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = EnrollmentRepository(db)

    async def add_documento(
        self,
        tenant_id: uuid.UUID,
        matricula_id: uuid.UUID,
        tipo: str,
        url: str,
    ) -> DocumentoMatricula:
        matricula = await self.repo.get_matricula(matricula_id, tenant_id)
        if matricula is None:
            raise NotFoundError("Matrícula não encontrada")

        doc = DocumentoMatricula(
            tenant_id=tenant_id,
            matricula_id=matricula_id,
            tipo=tipo,
            url=url,
        )
        doc = await self.repo.create_documento(doc)
        await self.db.commit()
        return doc

    async def list_documentos(
        self, matricula_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[DocumentoMatricula]:
        matricula = await self.repo.get_matricula(matricula_id, tenant_id)
        if matricula is None:
            raise NotFoundError("Matrícula não encontrada")
        return await self.repo.list_documentos(matricula_id, tenant_id)


# ── Domain Errors ───────────────────────────────

class EnrollmentError(Exception):
    pass


class NotFoundError(EnrollmentError):
    pass


class InvalidStateError(EnrollmentError):
    pass


class DuplicateMatriculaError(EnrollmentError):
    def __init__(self) -> None:
        super().__init__("Aluno já possui matrícula neste ano letivo")


class DuplicateAlocacaoError(EnrollmentError):
    def __init__(self) -> None:
        super().__init__("Esta matrícula já tem alocação em turma")