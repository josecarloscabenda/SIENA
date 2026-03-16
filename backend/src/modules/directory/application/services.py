"""Application services for the directory module."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.directory.infrastructure.models import (
    Aluno,
    Encarregado,
    Pessoa,
    Professor,
    VinculoAlunoEncarregado,
)
from src.modules.directory.infrastructure.repository import DirectoryRepository


class PessoaService:
    """Serviço para gestão de pessoas (alunos, professores, encarregados)."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = DirectoryRepository(db)

    # ── Alunos ──────────────────────────────────

    async def create_aluno(
        self,
        tenant_id: uuid.UUID,
        *,
        nome_completo: str,
        bi_identificacao: str,
        dt_nascimento: object,
        sexo: str,
        nacionalidade: str = "Angolana",
        morada: str | None = None,
        telefone: str | None = None,
        email: str | None = None,
        foto_url: str | None = None,
        n_processo: str,
        ano_ingresso: int,
        necessidades_especiais: bool = False,
        status: str = "ativo",
    ) -> Aluno:
        # Validar BI único no tenant
        existing = await self.repo.get_pessoa_by_bi(tenant_id, bi_identificacao)
        if existing:
            raise DuplicateBIError(bi_identificacao)

        # Validar n_processo único no tenant
        existing_aluno = await self.repo.get_aluno_by_n_processo(tenant_id, n_processo)
        if existing_aluno:
            raise DuplicateNProcessoError(n_processo)

        # Criar pessoa
        pessoa = Pessoa(
            tenant_id=tenant_id,
            nome_completo=nome_completo,
            bi_identificacao=bi_identificacao,
            dt_nascimento=dt_nascimento,
            sexo=sexo,
            nacionalidade=nacionalidade,
            morada=morada,
            telefone=telefone,
            email=email,
            foto_url=foto_url,
        )
        pessoa = await self.repo.create_pessoa(pessoa)

        # Criar aluno
        aluno = Aluno(
            tenant_id=tenant_id,
            pessoa_id=pessoa.id,
            n_processo=n_processo,
            ano_ingresso=ano_ingresso,
            necessidades_especiais=necessidades_especiais,
            status=status,
        )
        aluno = await self.repo.create_aluno(aluno)
        await self.db.commit()

        return await self.repo.get_aluno(aluno.id, tenant_id)  # type: ignore[return-value]

    async def get_aluno(self, aluno_id: uuid.UUID, tenant_id: uuid.UUID) -> Aluno | None:
        return await self.repo.get_aluno(aluno_id, tenant_id)

    async def get_aluno_detail(self, aluno_id: uuid.UUID, tenant_id: uuid.UUID) -> Aluno | None:
        return await self.repo.get_aluno_detail(aluno_id, tenant_id)

    async def list_alunos(
        self,
        tenant_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        nome: str | None = None,
        n_processo: str | None = None,
        status: str | None = None,
    ) -> tuple[list[Aluno], int]:
        return await self.repo.list_alunos(
            tenant_id, offset, limit, nome, n_processo, status
        )

    async def update_aluno(
        self,
        aluno_id: uuid.UUID,
        tenant_id: uuid.UUID,
        **fields: object,
    ) -> Aluno:
        aluno = await self.repo.get_aluno(aluno_id, tenant_id)
        if aluno is None:
            raise NotFoundError("Aluno não encontrado")

        pessoa_fields = {
            "nome_completo", "bi_identificacao", "dt_nascimento", "sexo",
            "nacionalidade", "morada", "telefone", "email", "foto_url",
        }
        aluno_fields = {"n_processo", "necessidades_especiais", "status"}

        # Validar BI se alterado
        if "bi_identificacao" in fields and fields["bi_identificacao"] is not None:
            existing = await self.repo.get_pessoa_by_bi(
                tenant_id, str(fields["bi_identificacao"])
            )
            if existing and existing.id != aluno.pessoa_id:
                raise DuplicateBIError(str(fields["bi_identificacao"]))

        # Validar n_processo se alterado
        if "n_processo" in fields and fields["n_processo"] is not None:
            existing_aluno = await self.repo.get_aluno_by_n_processo(
                tenant_id, str(fields["n_processo"])
            )
            if existing_aluno and existing_aluno.id != aluno_id:
                raise DuplicateNProcessoError(str(fields["n_processo"]))

        # Actualizar campos da pessoa
        pessoa = await self.repo.get_pessoa(aluno.pessoa_id, tenant_id)
        if pessoa:
            for key, value in fields.items():
                if key in pessoa_fields and value is not None:
                    setattr(pessoa, key, value)

        # Actualizar campos do aluno
        for key, value in fields.items():
            if key in aluno_fields and value is not None:
                setattr(aluno, key, value)

        await self.db.commit()
        return await self.repo.get_aluno(aluno_id, tenant_id)  # type: ignore[return-value]

    # ── Professores ─────────────────────────────

    async def create_professor(
        self,
        tenant_id: uuid.UUID,
        *,
        nome_completo: str,
        bi_identificacao: str,
        dt_nascimento: object,
        sexo: str,
        nacionalidade: str = "Angolana",
        morada: str | None = None,
        telefone: str | None = None,
        email: str | None = None,
        foto_url: str | None = None,
        codigo_funcional: str,
        especialidade: str,
        carga_horaria_semanal: int,
        tipo_contrato: str = "contrato",
        nivel_academico: str | None = None,
    ) -> Professor:
        existing = await self.repo.get_pessoa_by_bi(tenant_id, bi_identificacao)
        if existing:
            raise DuplicateBIError(bi_identificacao)

        pessoa = Pessoa(
            tenant_id=tenant_id,
            nome_completo=nome_completo,
            bi_identificacao=bi_identificacao,
            dt_nascimento=dt_nascimento,
            sexo=sexo,
            nacionalidade=nacionalidade,
            morada=morada,
            telefone=telefone,
            email=email,
            foto_url=foto_url,
        )
        pessoa = await self.repo.create_pessoa(pessoa)

        professor = Professor(
            tenant_id=tenant_id,
            pessoa_id=pessoa.id,
            codigo_funcional=codigo_funcional,
            especialidade=especialidade,
            carga_horaria_semanal=carga_horaria_semanal,
            tipo_contrato=tipo_contrato,
            nivel_academico=nivel_academico,
        )
        professor = await self.repo.create_professor(professor)
        await self.db.commit()

        return await self.repo.get_professor(professor.id, tenant_id)  # type: ignore[return-value]

    async def get_professor(
        self, professor_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Professor | None:
        return await self.repo.get_professor(professor_id, tenant_id)

    async def list_professores(
        self,
        tenant_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        especialidade: str | None = None,
        tipo_contrato: str | None = None,
    ) -> tuple[list[Professor], int]:
        return await self.repo.list_professores(
            tenant_id, offset, limit, especialidade, tipo_contrato
        )

    async def update_professor(
        self,
        professor_id: uuid.UUID,
        tenant_id: uuid.UUID,
        **fields: object,
    ) -> Professor:
        professor = await self.repo.get_professor(professor_id, tenant_id)
        if professor is None:
            raise NotFoundError("Professor não encontrado")

        pessoa_fields = {
            "nome_completo", "bi_identificacao", "dt_nascimento", "sexo",
            "nacionalidade", "morada", "telefone", "email", "foto_url",
        }
        prof_fields = {
            "codigo_funcional", "especialidade", "carga_horaria_semanal",
            "tipo_contrato", "nivel_academico",
        }

        if "bi_identificacao" in fields and fields["bi_identificacao"] is not None:
            existing = await self.repo.get_pessoa_by_bi(
                tenant_id, str(fields["bi_identificacao"])
            )
            if existing and existing.id != professor.pessoa_id:
                raise DuplicateBIError(str(fields["bi_identificacao"]))

        pessoa = await self.repo.get_pessoa(professor.pessoa_id, tenant_id)
        if pessoa:
            for key, value in fields.items():
                if key in pessoa_fields and value is not None:
                    setattr(pessoa, key, value)

        for key, value in fields.items():
            if key in prof_fields and value is not None:
                setattr(professor, key, value)

        await self.db.commit()
        return await self.repo.get_professor(professor_id, tenant_id)  # type: ignore[return-value]

    # ── Encarregados ────────────────────────────

    async def create_encarregado(
        self,
        tenant_id: uuid.UUID,
        *,
        nome_completo: str,
        bi_identificacao: str,
        dt_nascimento: object,
        sexo: str,
        nacionalidade: str = "Angolana",
        morada: str | None = None,
        telefone: str | None = None,
        email: str | None = None,
        foto_url: str | None = None,
        profissao: str | None = None,
        escolaridade: str | None = None,
    ) -> Encarregado:
        existing = await self.repo.get_pessoa_by_bi(tenant_id, bi_identificacao)
        if existing:
            raise DuplicateBIError(bi_identificacao)

        pessoa = Pessoa(
            tenant_id=tenant_id,
            nome_completo=nome_completo,
            bi_identificacao=bi_identificacao,
            dt_nascimento=dt_nascimento,
            sexo=sexo,
            nacionalidade=nacionalidade,
            morada=morada,
            telefone=telefone,
            email=email,
            foto_url=foto_url,
        )
        pessoa = await self.repo.create_pessoa(pessoa)

        encarregado = Encarregado(
            tenant_id=tenant_id,
            pessoa_id=pessoa.id,
            profissao=profissao,
            escolaridade=escolaridade,
        )
        encarregado = await self.repo.create_encarregado(encarregado)
        await self.db.commit()

        return await self.repo.get_encarregado(encarregado.id, tenant_id)  # type: ignore[return-value]

    async def list_encarregados(
        self,
        tenant_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Encarregado], int]:
        return await self.repo.list_encarregados(tenant_id, offset, limit)


class VinculoService:
    """Serviço para gestão de vínculos aluno ↔ encarregado."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = DirectoryRepository(db)

    async def create_vinculo(
        self,
        tenant_id: uuid.UUID,
        aluno_id: uuid.UUID,
        encarregado_id: uuid.UUID,
        tipo: str,
        principal: bool = False,
    ) -> VinculoAlunoEncarregado:
        # Validar aluno existe
        aluno = await self.repo.get_aluno(aluno_id, tenant_id)
        if aluno is None:
            raise NotFoundError("Aluno não encontrado")

        # Validar encarregado existe
        encarregado = await self.repo.get_encarregado(encarregado_id, tenant_id)
        if encarregado is None:
            raise NotFoundError("Encarregado não encontrado")

        # Validar duplicado
        existing = await self.repo.get_vinculo_existente(aluno_id, encarregado_id)
        if existing:
            raise DuplicateVinculoError()

        # Se marcado como principal, desmarcar os outros
        if principal:
            await self.repo.unset_principal(aluno_id, tenant_id)

        vinculo = VinculoAlunoEncarregado(
            tenant_id=tenant_id,
            aluno_id=aluno_id,
            encarregado_id=encarregado_id,
            tipo=tipo,
            principal=principal,
        )
        vinculo = await self.repo.create_vinculo(vinculo)
        await self.db.commit()
        return vinculo

    async def list_vinculos(
        self, aluno_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[VinculoAlunoEncarregado]:
        # Validar aluno existe
        aluno = await self.repo.get_aluno(aluno_id, tenant_id)
        if aluno is None:
            raise NotFoundError("Aluno não encontrado")
        return await self.repo.list_vinculos(aluno_id, tenant_id)


# ── Domain Errors ───────────────────────────────

class DirectoryError(Exception):
    pass


class NotFoundError(DirectoryError):
    pass


class DuplicateBIError(DirectoryError):
    def __init__(self, bi: str) -> None:
        super().__init__(f"BI '{bi}' já registado neste tenant")
        self.bi = bi


class DuplicateNProcessoError(DirectoryError):
    def __init__(self, n_processo: str) -> None:
        super().__init__(f"N.º de processo '{n_processo}' já existe neste tenant")
        self.n_processo = n_processo


class DuplicateVinculoError(DirectoryError):
    def __init__(self) -> None:
        super().__init__("Este vínculo aluno-encarregado já existe")