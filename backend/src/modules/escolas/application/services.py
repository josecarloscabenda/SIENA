"""Application services for the escolas module."""

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.common.utils.password import hash_password
from src.modules.directory.infrastructure.models import Pessoa
from src.modules.escolas.infrastructure.models import AnoLetivo, ConfiguracaoEscola, Escola, Infraestrutura
from src.modules.escolas.infrastructure.repository import EscolasRepository
from src.modules.identity.infrastructure.models import Papel, Tenant, Utilizador, UtilizadorPapel


class EscolaService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = EscolasRepository(db)

    async def create_escola_with_tenant(
        self,
        *,
        # Escola fields
        nome: str,
        provincia: str,
        municipio: str,
        tipo: str = "publica",
        nivel_ensino: str = "primario",
        codigo_sige: str | None = None,
        comuna: str | None = None,
        endereco: str | None = None,
        telefone: str | None = None,
        email: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        # Diretor pessoa fields
        diretor_nome_completo: str,
        diretor_bi: str,
        diretor_dt_nascimento: date,
        diretor_sexo: str,
        diretor_nacionalidade: str = "Angolana",
        diretor_morada: str | None = None,
        diretor_telefone: str | None = None,
        diretor_email: str | None = None,
        # Diretor user fields
        diretor_username: str,
        diretor_password: str,
    ) -> dict:
        """Super admin: create Tenant + Escola + Pessoa + Utilizador(diretor) in one operation."""
        if codigo_sige:
            existing = await self.repo.get_escola_by_codigo_sige(codigo_sige)
            if existing:
                raise ValueError(f"Código SIGE '{codigo_sige}' já existe")

        # 1. Create the Tenant
        tenant = Tenant(nome=nome, estado="ativo", plano="basico")
        self.db.add(tenant)
        await self.db.flush()

        # 2. Create the Escola within the new tenant
        escola = Escola(
            tenant_id=tenant.id,
            nome=nome,
            codigo_sige=codigo_sige,
            tipo=tipo,
            nivel_ensino=nivel_ensino,
            provincia=provincia,
            municipio=municipio,
            comuna=comuna,
            endereco=endereco,
            telefone=telefone,
            email=email,
            latitude=latitude,
            longitude=longitude,
        )
        self.db.add(escola)
        await self.db.flush()

        # 3. Create default ConfiguracaoEscola
        config = ConfiguracaoEscola(tenant_id=tenant.id, escola_id=escola.id)
        self.db.add(config)

        # 4. Create Pessoa for the diretor
        pessoa = Pessoa(
            tenant_id=tenant.id,
            nome_completo=diretor_nome_completo,
            bi_identificacao=diretor_bi,
            dt_nascimento=diretor_dt_nascimento,
            sexo=diretor_sexo,
            nacionalidade=diretor_nacionalidade,
            morada=diretor_morada,
            telefone=diretor_telefone,
            email=diretor_email,
        )
        self.db.add(pessoa)
        await self.db.flush()

        # 5. Create the diretor Utilizador linked to Pessoa
        diretor = Utilizador(
            tenant_id=tenant.id,
            pessoa_id=pessoa.id,
            username=diretor_username,
            senha_hash=hash_password(diretor_password),
            nome_completo=diretor_nome_completo,
            email=diretor_email,
            tipo="local",
            ativo=True,
        )
        self.db.add(diretor)
        await self.db.flush()

        # 6. Assign the "diretor" role
        papel_result = await self.db.execute(
            select(Papel).where(Papel.nome == "diretor")
        )
        papel_diretor = papel_result.scalar_one_or_none()
        if papel_diretor is None:
            raise ValueError("Papel 'diretor' não encontrado. Execute o seed de identity primeiro.")

        up = UtilizadorPapel(
            utilizador_id=diretor.id,
            papel_id=papel_diretor.id,
            tenant_id=tenant.id,
            ativo=True,
        )
        self.db.add(up)

        await self.db.commit()

        return {
            "tenant": tenant,
            "escola": escola,
            "pessoa": pessoa,
            "diretor": diretor,
        }

    async def create_escola(
        self,
        tenant_id: uuid.UUID,
        nome: str,
        provincia: str,
        municipio: str,
        tipo: str = "publica",
        nivel_ensino: str = "primario",
        codigo_sige: str | None = None,
        comuna: str | None = None,
        endereco: str | None = None,
        telefone: str | None = None,
        email: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> Escola:
        if codigo_sige:
            existing = await self.repo.get_escola_by_codigo_sige(codigo_sige)
            if existing:
                raise ValueError(f"Código SIGE '{codigo_sige}' já existe")

        escola = Escola(
            tenant_id=tenant_id,
            nome=nome,
            codigo_sige=codigo_sige,
            tipo=tipo,
            nivel_ensino=nivel_ensino,
            provincia=provincia,
            municipio=municipio,
            comuna=comuna,
            endereco=endereco,
            telefone=telefone,
            email=email,
            latitude=latitude,
            longitude=longitude,
        )
        escola = await self.repo.create_escola(escola)

        # Create default configuration
        config = ConfiguracaoEscola(
            tenant_id=tenant_id,
            escola_id=escola.id,
        )
        self.db.add(config)
        await self.db.commit()

        return await self.repo.get_escola(escola.id, tenant_id)  # type: ignore[return-value]

    async def get_escola(self, escola_id: uuid.UUID, tenant_id: uuid.UUID) -> Escola | None:
        return await self.repo.get_escola(escola_id, tenant_id)

    async def get_escola_global(self, escola_id: uuid.UUID) -> Escola | None:
        """Get escola without tenant filter (super_admin)."""
        return await self.repo.get_escola_global(escola_id)

    async def list_escolas(
        self,
        tenant_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        provincia: str | None = None,
        municipio: str | None = None,
    ) -> tuple[list[Escola], int]:
        return await self.repo.list_escolas(tenant_id, offset, limit, provincia, municipio)

    async def list_all_escolas(
        self,
        offset: int = 0,
        limit: int = 20,
        provincia: str | None = None,
    ) -> tuple[list[Escola], int]:
        """Super admin: list all escolas across tenants."""
        return await self.repo.list_all_escolas(offset, limit, provincia)

    async def update_escola(
        self,
        escola_id: uuid.UUID,
        tenant_id: uuid.UUID,
        **fields: str | float | bool | None,
    ) -> Escola:
        escola = await self.repo.get_escola(escola_id, tenant_id)
        if escola is None:
            raise ValueError("Escola não encontrada")

        if "codigo_sige" in fields and fields["codigo_sige"] is not None:
            existing = await self.repo.get_escola_by_codigo_sige(str(fields["codigo_sige"]))
            if existing and existing.id != escola_id:
                raise ValueError(f"Código SIGE '{fields['codigo_sige']}' já existe")

        for key, value in fields.items():
            if value is not None:
                setattr(escola, key, value)

        await self.db.commit()
        return await self.repo.get_escola(escola_id, tenant_id)  # type: ignore[return-value]

    async def abrir_ano_letivo(
        self,
        escola_id: uuid.UUID,
        tenant_id: uuid.UUID,
        ano: int,
        designacao: str,
        data_inicio: date,
        data_fim: date,
    ) -> AnoLetivo:
        escola = await self.repo.get_escola(escola_id, tenant_id)
        if escola is None:
            raise ValueError("Escola não encontrada")

        if data_fim <= data_inicio:
            raise ValueError("Data de fim deve ser posterior à data de início")

        # Deactivate any currently active ano letivo
        await self.repo.deactivate_anos_letivos(escola_id, tenant_id)

        ano_letivo = AnoLetivo(
            tenant_id=tenant_id,
            escola_id=escola_id,
            ano=ano,
            designacao=designacao,
            data_inicio=data_inicio,
            data_fim=data_fim,
            ativo=True,
        )
        ano_letivo = await self.repo.create_ano_letivo(ano_letivo)
        await self.db.commit()
        return ano_letivo

    async def list_infraestruturas(self, escola_id: uuid.UUID, tenant_id: uuid.UUID) -> list:
        escola = await self.repo.get_escola(escola_id, tenant_id)
        if escola is None:
            raise ValueError("Escola não encontrada")
        return await self.repo.list_infraestruturas(escola_id, tenant_id)

    async def create_infraestrutura(
        self,
        escola_id: uuid.UUID,
        tenant_id: uuid.UUID,
        nome: str,
        tipo: str = "sala_aula",
        capacidade: int | None = None,
        estado: str = "operacional",
        observacoes: str | None = None,
    ) -> Infraestrutura:
        escola = await self.repo.get_escola(escola_id, tenant_id)
        if escola is None:
            raise ValueError("Escola não encontrada")
        infra = Infraestrutura(
            tenant_id=tenant_id,
            escola_id=escola_id,
            nome=nome,
            tipo=tipo,
            capacidade=capacidade,
            estado=estado,
            observacoes=observacoes,
        )
        infra = await self.repo.create_infraestrutura(infra)
        await self.db.commit()
        return infra

    async def update_infraestrutura(
        self,
        infra_id: uuid.UUID,
        escola_id: uuid.UUID,
        tenant_id: uuid.UUID,
        **fields: str | int | None,
    ) -> Infraestrutura:
        infra = await self.repo.get_infraestrutura(infra_id, escola_id, tenant_id)
        if infra is None:
            raise ValueError("Infraestrutura não encontrada")
        for key, value in fields.items():
            if value is not None:
                setattr(infra, key, value)
        await self.db.commit()
        await self.db.refresh(infra)
        return infra

    async def delete_infraestrutura(
        self,
        infra_id: uuid.UUID,
        escola_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> None:
        from datetime import datetime, timezone
        infra = await self.repo.get_infraestrutura(infra_id, escola_id, tenant_id)
        if infra is None:
            raise ValueError("Infraestrutura não encontrada")
        infra.deleted_at = datetime.now(timezone.utc)
        await self.db.commit()