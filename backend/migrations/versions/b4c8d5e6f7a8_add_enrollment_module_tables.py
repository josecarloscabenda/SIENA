"""add enrollment module tables

Revision ID: b4c8d5e6f7a8
Revises: a3b7c2d4e5f6
Create Date: 2026-03-15 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b4c8d5e6f7a8'
down_revision: Union[str, None] = 'a3b7c2d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- matricula ---
    op.create_table('matricula',
        sa.Column('aluno_id', sa.UUID(), nullable=False),
        sa.Column('ano_letivo_id', sa.UUID(), nullable=False),
        sa.Column('classe', sa.String(length=10), nullable=False, comment='1.ª, 7.ª, 10.ª, etc.'),
        sa.Column('turno', sa.String(length=20), server_default='matutino', nullable=False, comment='matutino, vespertino, nocturno'),
        sa.Column('estado', sa.String(length=20), server_default='pendente', nullable=False, comment='pendente, aprovada, rejeitada, cancelada'),
        sa.Column('data_pedido', sa.Date(), nullable=False),
        sa.Column('data_aprovacao', sa.Date(), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['aluno_id'], ['directory.aluno.id'], ),
        sa.ForeignKeyConstraint(['ano_letivo_id'], ['escolas.ano_letivo.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'aluno_id', 'ano_letivo_id', name='uq_matricula_tenant_aluno_ano'),
        schema='enrollment'
    )
    op.create_index(op.f('ix_enrollment_matricula_aluno_id'), 'matricula', ['aluno_id'], unique=False, schema='enrollment')
    op.create_index(op.f('ix_enrollment_matricula_ano_letivo_id'), 'matricula', ['ano_letivo_id'], unique=False, schema='enrollment')
    op.create_index(op.f('ix_enrollment_matricula_tenant_id'), 'matricula', ['tenant_id'], unique=False, schema='enrollment')

    # --- alocacao_turma ---
    op.create_table('alocacao_turma',
        sa.Column('matricula_id', sa.UUID(), nullable=False),
        sa.Column('turma_id', sa.UUID(), nullable=False, comment='FK para academico.turma (cross-schema, sem constraint)'),
        sa.Column('data_alocacao', sa.Date(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['matricula_id'], ['enrollment.matricula.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='enrollment'
    )
    op.create_index(op.f('ix_enrollment_alocacao_turma_matricula_id'), 'alocacao_turma', ['matricula_id'], unique=False, schema='enrollment')
    op.create_index(op.f('ix_enrollment_alocacao_turma_tenant_id'), 'alocacao_turma', ['tenant_id'], unique=False, schema='enrollment')
    op.create_index(op.f('ix_enrollment_alocacao_turma_turma_id'), 'alocacao_turma', ['turma_id'], unique=False, schema='enrollment')

    # --- transferencia ---
    op.create_table('transferencia',
        sa.Column('aluno_id', sa.UUID(), nullable=False),
        sa.Column('escola_origem_id', sa.UUID(), nullable=False),
        sa.Column('escola_destino_id', sa.UUID(), nullable=False),
        sa.Column('data_pedido', sa.Date(), nullable=False),
        sa.Column('estado', sa.String(length=20), server_default='pendente', nullable=False, comment='pendente, aprovada, rejeitada, cancelada'),
        sa.Column('motivo', sa.Text(), nullable=False),
        sa.Column('documentos_url', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Array de URLs S3'),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['aluno_id'], ['directory.aluno.id'], ),
        sa.ForeignKeyConstraint(['escola_destino_id'], ['escolas.escola.id'], ),
        sa.ForeignKeyConstraint(['escola_origem_id'], ['escolas.escola.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='enrollment'
    )
    op.create_index(op.f('ix_enrollment_transferencia_aluno_id'), 'transferencia', ['aluno_id'], unique=False, schema='enrollment')
    op.create_index(op.f('ix_enrollment_transferencia_tenant_id'), 'transferencia', ['tenant_id'], unique=False, schema='enrollment')

    # --- documento_matricula ---
    op.create_table('documento_matricula',
        sa.Column('matricula_id', sa.UUID(), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=False, comment='cartao_cidadao, atestado_vacinacao, foto, etc.'),
        sa.Column('url', sa.String(length=500), nullable=False, comment='Referência S3'),
        sa.Column('verificado', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['matricula_id'], ['enrollment.matricula.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='enrollment'
    )
    op.create_index(op.f('ix_enrollment_documento_matricula_matricula_id'), 'documento_matricula', ['matricula_id'], unique=False, schema='enrollment')
    op.create_index(op.f('ix_enrollment_documento_matricula_tenant_id'), 'documento_matricula', ['tenant_id'], unique=False, schema='enrollment')


def downgrade() -> None:
    op.drop_index(op.f('ix_enrollment_documento_matricula_tenant_id'), table_name='documento_matricula', schema='enrollment')
    op.drop_index(op.f('ix_enrollment_documento_matricula_matricula_id'), table_name='documento_matricula', schema='enrollment')
    op.drop_table('documento_matricula', schema='enrollment')
    op.drop_index(op.f('ix_enrollment_transferencia_tenant_id'), table_name='transferencia', schema='enrollment')
    op.drop_index(op.f('ix_enrollment_transferencia_aluno_id'), table_name='transferencia', schema='enrollment')
    op.drop_table('transferencia', schema='enrollment')
    op.drop_index(op.f('ix_enrollment_alocacao_turma_turma_id'), table_name='alocacao_turma', schema='enrollment')
    op.drop_index(op.f('ix_enrollment_alocacao_turma_tenant_id'), table_name='alocacao_turma', schema='enrollment')
    op.drop_index(op.f('ix_enrollment_alocacao_turma_matricula_id'), table_name='alocacao_turma', schema='enrollment')
    op.drop_table('alocacao_turma', schema='enrollment')
    op.drop_index(op.f('ix_enrollment_matricula_tenant_id'), table_name='matricula', schema='enrollment')
    op.drop_index(op.f('ix_enrollment_matricula_ano_letivo_id'), table_name='matricula', schema='enrollment')
    op.drop_index(op.f('ix_enrollment_matricula_aluno_id'), table_name='matricula', schema='enrollment')
    op.drop_table('matricula', schema='enrollment')
