"""add academico module tables

Revision ID: c5d9e0f1a2b3
Revises: b4c8d5e6f7a8
Create Date: 2026-03-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c5d9e0f1a2b3'
down_revision: Union[str, None] = 'b4c8d5e6f7a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- curriculo ---
    op.create_table('curriculo',
        sa.Column('nivel', sa.String(length=50), nullable=False, comment='primario, secundario_1ciclo, etc.'),
        sa.Column('classe', sa.String(length=10), nullable=False),
        sa.Column('ano_letivo_id', sa.UUID(), nullable=False),
        sa.Column('carga_horaria_total', sa.Integer(), nullable=False, comment='Horas semanais'),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['ano_letivo_id'], ['escolas.ano_letivo.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='academico'
    )
    op.create_index(op.f('ix_academico_curriculo_ano_letivo_id'), 'curriculo', ['ano_letivo_id'], unique=False, schema='academico')
    op.create_index(op.f('ix_academico_curriculo_tenant_id'), 'curriculo', ['tenant_id'], unique=False, schema='academico')

    # --- disciplina ---
    op.create_table('disciplina',
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('codigo', sa.String(length=50), nullable=False, comment='Único por tenant'),
        sa.Column('curriculo_id', sa.UUID(), nullable=False),
        sa.Column('carga_horaria_semanal', sa.Integer(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['curriculo_id'], ['academico.curriculo.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'codigo', name='uq_disciplina_tenant_codigo'),
        schema='academico'
    )
    op.create_index(op.f('ix_academico_disciplina_curriculo_id'), 'disciplina', ['curriculo_id'], unique=False, schema='academico')
    op.create_index(op.f('ix_academico_disciplina_tenant_id'), 'disciplina', ['tenant_id'], unique=False, schema='academico')

    # --- turma ---
    op.create_table('turma',
        sa.Column('nome', sa.String(length=50), nullable=False, comment='7.ª-A, 10.ª-B, etc.'),
        sa.Column('classe', sa.String(length=10), nullable=False),
        sa.Column('turno', sa.String(length=20), nullable=False, comment='matutino, vespertino, nocturno'),
        sa.Column('ano_letivo_id', sa.UUID(), nullable=False),
        sa.Column('capacidade_max', sa.Integer(), nullable=False),
        sa.Column('professor_regente_id', sa.UUID(), nullable=False),
        sa.Column('sala', sa.String(length=100), nullable=True, comment='Sala/infraestrutura'),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['ano_letivo_id'], ['escolas.ano_letivo.id'], ),
        sa.ForeignKeyConstraint(['professor_regente_id'], ['directory.professor.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='academico'
    )
    op.create_index(op.f('ix_academico_turma_ano_letivo_id'), 'turma', ['ano_letivo_id'], unique=False, schema='academico')
    op.create_index(op.f('ix_academico_turma_professor_regente_id'), 'turma', ['professor_regente_id'], unique=False, schema='academico')
    op.create_index(op.f('ix_academico_turma_tenant_id'), 'turma', ['tenant_id'], unique=False, schema='academico')

    # --- horario_aula ---
    op.create_table('horario_aula',
        sa.Column('turma_id', sa.UUID(), nullable=False),
        sa.Column('disciplina_id', sa.UUID(), nullable=False),
        sa.Column('professor_id', sa.UUID(), nullable=False),
        sa.Column('dia_semana', sa.String(length=10), nullable=False, comment='segunda, terca, quarta, quinta, sexta, sabado'),
        sa.Column('hora_inicio', sa.Time(), nullable=False),
        sa.Column('hora_fim', sa.Time(), nullable=False),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['disciplina_id'], ['academico.disciplina.id'], ),
        sa.ForeignKeyConstraint(['professor_id'], ['directory.professor.id'], ),
        sa.ForeignKeyConstraint(['turma_id'], ['academico.turma.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='academico'
    )
    op.create_index(op.f('ix_academico_horario_aula_disciplina_id'), 'horario_aula', ['disciplina_id'], unique=False, schema='academico')
    op.create_index(op.f('ix_academico_horario_aula_professor_id'), 'horario_aula', ['professor_id'], unique=False, schema='academico')
    op.create_index(op.f('ix_academico_horario_aula_tenant_id'), 'horario_aula', ['tenant_id'], unique=False, schema='academico')
    op.create_index(op.f('ix_academico_horario_aula_turma_id'), 'horario_aula', ['turma_id'], unique=False, schema='academico')

    # --- diario_classe ---
    op.create_table('diario_classe',
        sa.Column('turma_id', sa.UUID(), nullable=False),
        sa.Column('disciplina_id', sa.UUID(), nullable=False),
        sa.Column('professor_id', sa.UUID(), nullable=False),
        sa.Column('data_aula', sa.Date(), nullable=False),
        sa.Column('conteudo', sa.Text(), nullable=False, comment='Conteúdo leccionado'),
        sa.Column('sumario', sa.Text(), nullable=False, comment='Sumário da aula'),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['disciplina_id'], ['academico.disciplina.id'], ),
        sa.ForeignKeyConstraint(['professor_id'], ['directory.professor.id'], ),
        sa.ForeignKeyConstraint(['turma_id'], ['academico.turma.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='academico'
    )
    op.create_index(op.f('ix_academico_diario_classe_disciplina_id'), 'diario_classe', ['disciplina_id'], unique=False, schema='academico')
    op.create_index(op.f('ix_academico_diario_classe_professor_id'), 'diario_classe', ['professor_id'], unique=False, schema='academico')
    op.create_index(op.f('ix_academico_diario_classe_tenant_id'), 'diario_classe', ['tenant_id'], unique=False, schema='academico')
    op.create_index(op.f('ix_academico_diario_classe_turma_id'), 'diario_classe', ['turma_id'], unique=False, schema='academico')

    # --- presenca_diario ---
    op.create_table('presenca_diario',
        sa.Column('diario_id', sa.UUID(), nullable=False),
        sa.Column('aluno_id', sa.UUID(), nullable=False),
        sa.Column('presente', sa.Boolean(), nullable=False),
        sa.Column('justificativa', sa.Text(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['aluno_id'], ['directory.aluno.id'], ),
        sa.ForeignKeyConstraint(['diario_id'], ['academico.diario_classe.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='academico'
    )
    op.create_index(op.f('ix_academico_presenca_diario_aluno_id'), 'presenca_diario', ['aluno_id'], unique=False, schema='academico')
    op.create_index(op.f('ix_academico_presenca_diario_diario_id'), 'presenca_diario', ['diario_id'], unique=False, schema='academico')
    op.create_index(op.f('ix_academico_presenca_diario_tenant_id'), 'presenca_diario', ['tenant_id'], unique=False, schema='academico')


def downgrade() -> None:
    op.drop_index(op.f('ix_academico_presenca_diario_tenant_id'), table_name='presenca_diario', schema='academico')
    op.drop_index(op.f('ix_academico_presenca_diario_diario_id'), table_name='presenca_diario', schema='academico')
    op.drop_index(op.f('ix_academico_presenca_diario_aluno_id'), table_name='presenca_diario', schema='academico')
    op.drop_table('presenca_diario', schema='academico')
    op.drop_index(op.f('ix_academico_diario_classe_turma_id'), table_name='diario_classe', schema='academico')
    op.drop_index(op.f('ix_academico_diario_classe_tenant_id'), table_name='diario_classe', schema='academico')
    op.drop_index(op.f('ix_academico_diario_classe_professor_id'), table_name='diario_classe', schema='academico')
    op.drop_index(op.f('ix_academico_diario_classe_disciplina_id'), table_name='diario_classe', schema='academico')
    op.drop_table('diario_classe', schema='academico')
    op.drop_index(op.f('ix_academico_horario_aula_turma_id'), table_name='horario_aula', schema='academico')
    op.drop_index(op.f('ix_academico_horario_aula_tenant_id'), table_name='horario_aula', schema='academico')
    op.drop_index(op.f('ix_academico_horario_aula_professor_id'), table_name='horario_aula', schema='academico')
    op.drop_index(op.f('ix_academico_horario_aula_disciplina_id'), table_name='horario_aula', schema='academico')
    op.drop_table('horario_aula', schema='academico')
    op.drop_index(op.f('ix_academico_turma_tenant_id'), table_name='turma', schema='academico')
    op.drop_index(op.f('ix_academico_turma_professor_regente_id'), table_name='turma', schema='academico')
    op.drop_index(op.f('ix_academico_turma_ano_letivo_id'), table_name='turma', schema='academico')
    op.drop_table('turma', schema='academico')
    op.drop_index(op.f('ix_academico_disciplina_tenant_id'), table_name='disciplina', schema='academico')
    op.drop_index(op.f('ix_academico_disciplina_curriculo_id'), table_name='disciplina', schema='academico')
    op.drop_table('disciplina', schema='academico')
    op.drop_index(op.f('ix_academico_curriculo_tenant_id'), table_name='curriculo', schema='academico')
    op.drop_index(op.f('ix_academico_curriculo_ano_letivo_id'), table_name='curriculo', schema='academico')
    op.drop_table('curriculo', schema='academico')
