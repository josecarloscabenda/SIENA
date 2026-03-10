import uuid
from datetime import datetime

from sqlalchemy import DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TenantMixin:
    """Mixin para todas as tabelas multi-tenant."""

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )


class TimestampMixin:
    """Mixin para created_at e updated_at."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        onupdate=text("now()"),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin para soft delete."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )


class BaseModel(Base, TimestampMixin, SoftDeleteMixin):
    """Base para todas as entidades do SIENA."""

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class TenantBaseModel(BaseModel, TenantMixin):
    """Base para tabelas de negócio com tenant isolation."""

    __abstract__ = True
