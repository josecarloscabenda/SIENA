"""Application services for the escolas module."""

import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.escolas.infrastructure.models import AnoLetivo, ConfiguracaoEscola, Escola
from src.modules.escolas.infrastructure.repository import EscolasRepository


class EscolaService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = EscolasRepository(db)

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

    async def list_escolas(
        self,
        tenant_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
        provincia: str | None = None,
        municipio: str | None = None,
    ) -> tuple[list[Escola], int]:
        return await self.repo.list_escolas(tenant_id, offset, limit, provincia, municipio)

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