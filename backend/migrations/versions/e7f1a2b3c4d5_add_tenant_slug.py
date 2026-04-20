"""add slug column to tenant

Revision ID: e7f1a2b3c4d5
Revises: d6e0f1a2b3c4
Create Date: 2026-04-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e7f1a2b3c4d5'
down_revision: Union[str, None] = 'd6e0f1a2b3c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add slug column as nullable first, backfill, then set NOT NULL + UNIQUE
    op.add_column(
        'tenant',
        sa.Column(
            'slug',
            sa.String(length=100),
            nullable=True,
            comment='Identificador URL-friendly da escola (ex: esa-luanda-1)',
        ),
        schema='identity',
    )

    # Backfill: generate slug from nome (lowercase, spaces -> hyphens, strip non-alphanumeric)
    op.execute(
        """
        UPDATE identity.tenant
        SET slug = LOWER(
            REGEXP_REPLACE(
                REGEXP_REPLACE(
                    TRANSLATE(nome,
                        'àáâãäåèéêëìíîïòóôõöùúûüýÿñç',
                        'aaaaaaeeeeiiiiooooouuuuyync'),
                    '[^a-zA-Z0-9\\s-]', '', 'g'
                ),
                '\\s+', '-', 'g'
            )
        )
        WHERE slug IS NULL
        """
    )

    # Fallback: if any tenant still has empty slug, use id
    op.execute(
        """
        UPDATE identity.tenant
        SET slug = 'tenant-' || SUBSTRING(id::text, 1, 8)
        WHERE slug IS NULL OR slug = ''
        """
    )

    # Set NOT NULL + UNIQUE
    op.alter_column('tenant', 'slug', nullable=False, schema='identity')
    op.create_unique_constraint(
        'uq_tenant_slug', 'tenant', ['slug'], schema='identity'
    )


def downgrade() -> None:
    op.drop_constraint('uq_tenant_slug', 'tenant', schema='identity', type_='unique')
    op.drop_column('tenant', 'slug', schema='identity')
