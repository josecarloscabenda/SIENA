"""add avaliacoes module tables

Revision ID: d6e0f1a2b3c4
Revises: c5d9e0f1a2b3
Create Date: 2026-03-15 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd6e0f1a2b3c4'
down_revision: Union[str, None] = 'c5d9e0f1a2b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- avaliacao ---
    op.create_table('avaliacao',
        sa.Column('turma_id', sa.UUID(), nullable=False),
        sa.Column('disciplina_id', sa.UUID(), nullable=False),
        sa.Column('tipo', sa.String(length=20), nullable=False, comment='teste, trabalho, exame, oral'),
        sa.Column('periodo', sa.Integer(), nullable=False, comment='1, 2 ou 3'),
        sa.Column('data', sa.Date(), nullable=False),
        sa.Column('peso', sa.Float(), nullable=False, comment='Peso na média final'),
        sa.Column('nota_maxima', sa.Integer(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['disciplina_id'], ['academico.disciplina.id'], ),
        sa.ForeignKeyConstraint(['turma_id'], ['academico.turma.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='avaliacoes'
    )
    op.create_index(op.f('ix_avaliacoes_avaliacao_disciplina_id'), 'avaliacao', ['disciplina_id'], unique=False, schema='avaliacoes')
    op.create_index(op.f('ix_avaliacoes_avaliacao_tenant_id'), 'avaliacao', ['tenant_id'], unique=False, schema='avaliacoes')
    op.create_index(op.f('ix_avaliacoes_avaliacao_turma_id'), 'avaliacao', ['turma_id'], unique=False, schema='avaliacoes')

    # --- nota ---
    op.create_table('nota',
        sa.Column('avaliacao_id', sa.UUID(), nullable=False),
        sa.Column('aluno_id', sa.UUID(), nullable=False),
        sa.Column('valor', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('lancado_por', sa.UUID(), nullable=False, comment='Professor que lançou'),
        sa.Column('lancado_em', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['aluno_id'], ['directory.aluno.id'], ),
        sa.ForeignKeyConstraint(['avaliacao_id'], ['avaliacoes.avaliacao.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('avaliacao_id', 'aluno_id', name='uq_nota_avaliacao_aluno'),
        schema='avaliacoes'
    )
    op.create_index(op.f('ix_avaliacoes_nota_aluno_id'), 'nota', ['aluno_id'], unique=False, schema='avaliacoes')
    op.create_index(op.f('ix_avaliacoes_nota_avaliacao_id'), 'nota', ['avaliacao_id'], unique=False, schema='avaliacoes')
    op.create_index(op.f('ix_avaliacoes_nota_tenant_id'), 'nota', ['tenant_id'], unique=False, schema='avaliacoes')

    # --- falta ---
    op.create_table('falta',
        sa.Column('aluno_id', sa.UUID(), nullable=False),
        sa.Column('turma_id', sa.UUID(), nullable=False),
        sa.Column('disciplina_id', sa.UUID(), nullable=False),
        sa.Column('data', sa.Date(), nullable=False),
        sa.Column('tipo', sa.String(length=20), nullable=False, comment='justificada, injustificada'),
        sa.Column('justificativa', sa.Text(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['aluno_id'], ['directory.aluno.id'], ),
        sa.ForeignKeyConstraint(['disciplina_id'], ['academico.disciplina.id'], ),
        sa.ForeignKeyConstraint(['turma_id'], ['academico.turma.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='avaliacoes'
    )
    op.create_index(op.f('ix_avaliacoes_falta_aluno_id'), 'falta', ['aluno_id'], unique=False, schema='avaliacoes')
    op.create_index(op.f('ix_avaliacoes_falta_disciplina_id'), 'falta', ['disciplina_id'], unique=False, schema='avaliacoes')
    op.create_index(op.f('ix_avaliacoes_falta_tenant_id'), 'falta', ['tenant_id'], unique=False, schema='avaliacoes')
    op.create_index(op.f('ix_avaliacoes_falta_turma_id'), 'falta', ['turma_id'], unique=False, schema='avaliacoes')

    # --- regra_media ---
    op.create_table('regra_media',
        sa.Column('nivel', sa.String(length=50), nullable=False),
        sa.Column('disciplina_id', sa.UUID(), nullable=True, comment='NULL = todas'),
        sa.Column('formula', sa.String(length=500), nullable=False, comment='Fórmula de cálculo'),
        sa.Column('minimo_aprovacao', sa.Integer(), nullable=False),
        sa.Column('politica_recuperacao', sa.Text(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['disciplina_id'], ['academico.disciplina.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='avaliacoes'
    )
    op.create_index(op.f('ix_avaliacoes_regra_media_disciplina_id'), 'regra_media', ['disciplina_id'], unique=False, schema='avaliacoes')
    op.create_index(op.f('ix_avaliacoes_regra_media_tenant_id'), 'regra_media', ['tenant_id'], unique=False, schema='avaliacoes')

    # --- boletim ---
    op.create_table('boletim',
        sa.Column('aluno_id', sa.UUID(), nullable=False),
        sa.Column('ano_letivo_id', sa.UUID(), nullable=False),
        sa.Column('periodo', sa.Integer(), nullable=False),
        sa.Column('gerado_em', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('url_pdf', sa.String(length=500), nullable=False, comment='Referência S3'),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['aluno_id'], ['directory.aluno.id'], ),
        sa.ForeignKeyConstraint(['ano_letivo_id'], ['escolas.ano_letivo.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='avaliacoes'
    )
    op.create_index(op.f('ix_avaliacoes_boletim_aluno_id'), 'boletim', ['aluno_id'], unique=False, schema='avaliacoes')
    op.create_index(op.f('ix_avaliacoes_boletim_ano_letivo_id'), 'boletim', ['ano_letivo_id'], unique=False, schema='avaliacoes')
    op.create_index(op.f('ix_avaliacoes_boletim_tenant_id'), 'boletim', ['tenant_id'], unique=False, schema='avaliacoes')


def downgrade() -> None:
    op.drop_index(op.f('ix_avaliacoes_boletim_tenant_id'), table_name='boletim', schema='avaliacoes')
    op.drop_index(op.f('ix_avaliacoes_boletim_ano_letivo_id'), table_name='boletim', schema='avaliacoes')
    op.drop_index(op.f('ix_avaliacoes_boletim_aluno_id'), table_name='boletim', schema='avaliacoes')
    op.drop_table('boletim', schema='avaliacoes')
    op.drop_index(op.f('ix_avaliacoes_regra_media_tenant_id'), table_name='regra_media', schema='avaliacoes')
    op.drop_index(op.f('ix_avaliacoes_regra_media_disciplina_id'), table_name='regra_media', schema='avaliacoes')
    op.drop_table('regra_media', schema='avaliacoes')
    op.drop_index(op.f('ix_avaliacoes_falta_turma_id'), table_name='falta', schema='avaliacoes')
    op.drop_index(op.f('ix_avaliacoes_falta_tenant_id'), table_name='falta', schema='avaliacoes')
    op.drop_index(op.f('ix_avaliacoes_falta_disciplina_id'), table_name='falta', schema='avaliacoes')
    op.drop_index(op.f('ix_avaliacoes_falta_aluno_id'), table_name='falta', schema='avaliacoes')
    op.drop_table('falta', schema='avaliacoes')
    op.drop_index(op.f('ix_avaliacoes_nota_tenant_id'), table_name='nota', schema='avaliacoes')
    op.drop_index(op.f('ix_avaliacoes_nota_avaliacao_id'), table_name='nota', schema='avaliacoes')
    op.drop_index(op.f('ix_avaliacoes_nota_aluno_id'), table_name='nota', schema='avaliacoes')
    op.drop_table('nota', schema='avaliacoes')
    op.drop_index(op.f('ix_avaliacoes_avaliacao_turma_id'), table_name='avaliacao', schema='avaliacoes')
    op.drop_index(op.f('ix_avaliacoes_avaliacao_tenant_id'), table_name='avaliacao', schema='avaliacoes')
    op.drop_index(op.f('ix_avaliacoes_avaliacao_disciplina_id'), table_name='avaliacao', schema='avaliacoes')
    op.drop_table('avaliacao', schema='avaliacoes')
