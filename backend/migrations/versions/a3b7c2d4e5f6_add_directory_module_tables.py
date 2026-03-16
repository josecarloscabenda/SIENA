"""add directory module tables

Revision ID: a3b7c2d4e5f6
Revises: 1efdf44b838c
Create Date: 2026-03-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a3b7c2d4e5f6'
down_revision: Union[str, None] = '1efdf44b838c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- pessoa ---
    op.create_table('pessoa',
        sa.Column('nome_completo', sa.String(length=255), nullable=False),
        sa.Column('bi_identificacao', sa.String(length=50), nullable=False, comment='BI / Cartão de Cidadão'),
        sa.Column('dt_nascimento', sa.Date(), nullable=False),
        sa.Column('sexo', sa.String(length=1), nullable=False, comment='M, F'),
        sa.Column('nacionalidade', sa.String(length=100), server_default='Angolana', nullable=False),
        sa.Column('morada', sa.Text(), nullable=True),
        sa.Column('telefone', sa.String(length=30), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('foto_url', sa.String(length=500), nullable=True, comment='Referência S3'),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'bi_identificacao', name='uq_pessoa_tenant_bi'),
        schema='directory'
    )
    op.create_index(op.f('ix_directory_pessoa_tenant_id'), 'pessoa', ['tenant_id'], unique=False, schema='directory')

    # --- aluno ---
    op.create_table('aluno',
        sa.Column('pessoa_id', sa.UUID(), nullable=False),
        sa.Column('n_processo', sa.String(length=50), nullable=False, comment='Número de processo'),
        sa.Column('ano_ingresso', sa.Integer(), nullable=False),
        sa.Column('necessidades_especiais', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('status', sa.String(length=20), server_default='ativo', nullable=False, comment='ativo, transferido, desistente, concluinte'),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['pessoa_id'], ['directory.pessoa.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'n_processo', name='uq_aluno_tenant_nprocesso'),
        schema='directory'
    )
    op.create_index(op.f('ix_directory_aluno_pessoa_id'), 'aluno', ['pessoa_id'], unique=False, schema='directory')
    op.create_index(op.f('ix_directory_aluno_tenant_id'), 'aluno', ['tenant_id'], unique=False, schema='directory')

    # --- professor ---
    op.create_table('professor',
        sa.Column('pessoa_id', sa.UUID(), nullable=False),
        sa.Column('codigo_funcional', sa.String(length=50), nullable=False),
        sa.Column('especialidade', sa.String(length=100), nullable=False, comment='Área de formação'),
        sa.Column('carga_horaria_semanal', sa.Integer(), nullable=False),
        sa.Column('tipo_contrato', sa.String(length=20), server_default='contrato', nullable=False, comment='efetivo, contrato, substituto'),
        sa.Column('nivel_academico', sa.String(length=100), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['pessoa_id'], ['directory.pessoa.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='directory'
    )
    op.create_index(op.f('ix_directory_professor_pessoa_id'), 'professor', ['pessoa_id'], unique=False, schema='directory')
    op.create_index(op.f('ix_directory_professor_tenant_id'), 'professor', ['tenant_id'], unique=False, schema='directory')

    # --- encarregado ---
    op.create_table('encarregado',
        sa.Column('pessoa_id', sa.UUID(), nullable=False),
        sa.Column('profissao', sa.String(length=100), nullable=True),
        sa.Column('escolaridade', sa.String(length=50), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['pessoa_id'], ['directory.pessoa.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='directory'
    )
    op.create_index(op.f('ix_directory_encarregado_pessoa_id'), 'encarregado', ['pessoa_id'], unique=False, schema='directory')
    op.create_index(op.f('ix_directory_encarregado_tenant_id'), 'encarregado', ['tenant_id'], unique=False, schema='directory')

    # --- funcionario ---
    op.create_table('funcionario',
        sa.Column('pessoa_id', sa.UUID(), nullable=False),
        sa.Column('cargo', sa.String(length=100), nullable=False),
        sa.Column('departamento', sa.String(length=100), nullable=False),
        sa.Column('data_admissao', sa.Date(), nullable=False),
        sa.Column('tipo_contrato', sa.String(length=20), server_default='contrato', nullable=False, comment='efetivo, contrato'),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['pessoa_id'], ['directory.pessoa.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='directory'
    )
    op.create_index(op.f('ix_directory_funcionario_pessoa_id'), 'funcionario', ['pessoa_id'], unique=False, schema='directory')
    op.create_index(op.f('ix_directory_funcionario_tenant_id'), 'funcionario', ['tenant_id'], unique=False, schema='directory')

    # --- vinculo_aluno_encarregado ---
    op.create_table('vinculo_aluno_encarregado',
        sa.Column('aluno_id', sa.UUID(), nullable=False),
        sa.Column('encarregado_id', sa.UUID(), nullable=False),
        sa.Column('tipo', sa.String(length=20), nullable=False, comment='pai, mae, tutor, outro'),
        sa.Column('principal', sa.Boolean(), server_default='false', nullable=False, comment='Encarregado principal'),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['aluno_id'], ['directory.aluno.id'], ),
        sa.ForeignKeyConstraint(['encarregado_id'], ['directory.encarregado.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('aluno_id', 'encarregado_id', name='uq_vinculo_aluno_enc'),
        schema='directory'
    )
    op.create_index(op.f('ix_directory_vinculo_aluno_encarregado_aluno_id'), 'vinculo_aluno_encarregado', ['aluno_id'], unique=False, schema='directory')
    op.create_index(op.f('ix_directory_vinculo_aluno_encarregado_encarregado_id'), 'vinculo_aluno_encarregado', ['encarregado_id'], unique=False, schema='directory')
    op.create_index(op.f('ix_directory_vinculo_aluno_encarregado_tenant_id'), 'vinculo_aluno_encarregado', ['tenant_id'], unique=False, schema='directory')


def downgrade() -> None:
    op.drop_index(op.f('ix_directory_vinculo_aluno_encarregado_tenant_id'), table_name='vinculo_aluno_encarregado', schema='directory')
    op.drop_index(op.f('ix_directory_vinculo_aluno_encarregado_encarregado_id'), table_name='vinculo_aluno_encarregado', schema='directory')
    op.drop_index(op.f('ix_directory_vinculo_aluno_encarregado_aluno_id'), table_name='vinculo_aluno_encarregado', schema='directory')
    op.drop_table('vinculo_aluno_encarregado', schema='directory')
    op.drop_index(op.f('ix_directory_funcionario_tenant_id'), table_name='funcionario', schema='directory')
    op.drop_index(op.f('ix_directory_funcionario_pessoa_id'), table_name='funcionario', schema='directory')
    op.drop_table('funcionario', schema='directory')
    op.drop_index(op.f('ix_directory_encarregado_tenant_id'), table_name='encarregado', schema='directory')
    op.drop_index(op.f('ix_directory_encarregado_pessoa_id'), table_name='encarregado', schema='directory')
    op.drop_table('encarregado', schema='directory')
    op.drop_index(op.f('ix_directory_professor_tenant_id'), table_name='professor', schema='directory')
    op.drop_index(op.f('ix_directory_professor_pessoa_id'), table_name='professor', schema='directory')
    op.drop_table('professor', schema='directory')
    op.drop_index(op.f('ix_directory_aluno_tenant_id'), table_name='aluno', schema='directory')
    op.drop_index(op.f('ix_directory_aluno_pessoa_id'), table_name='aluno', schema='directory')
    op.drop_table('aluno', schema='directory')
    op.drop_index(op.f('ix_directory_pessoa_tenant_id'), table_name='pessoa', schema='directory')
    op.drop_table('pessoa', schema='directory')