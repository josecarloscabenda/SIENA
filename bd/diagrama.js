/* ============================================
   SIENA - Diagrama Interactivo do Modelo Relacional
   ============================================ */

const DOMAINS = [
  {
    id: 'identity',
    name: 'Identity',
    desc: 'Autenticacao, utilizadores, papeis e permissoes multi-tenant',
    color: 'identity',
    tables: [
      { name: 'tenant', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'nome', t: 'varchar(255)', nn: true, note: 'Nome da escola/organizacao' },
        { n: 'estado', t: 'varchar(20)', nn: true, def: 'ativo', note: 'ativo, suspenso, inativo' },
        { n: 'configuracao', t: 'jsonb', def: '{}' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'utilizador', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'pessoa_id', t: 'uuid', fk: 'directory.pessoa', note: 'FK futura' },
        { n: 'username', t: 'varchar(100)', nn: true },
        { n: 'senha_hash', t: 'varchar(255)', nn: true, note: 'bcrypt (cost >= 12)' },
        { n: 'nome_completo', t: 'varchar(255)', nn: true },
        { n: 'email', t: 'varchar(255)' },
        { n: 'tipo', t: 'varchar(30)', def: 'local', note: 'local, oidc' },
        { n: 'ativo', t: 'boolean', def: 'true' },
        { n: 'mfa_segredo', t: 'varchar(255)', note: 'TOTP secret' },
        { n: 'ultimo_login', t: 'timestamptz' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'papel', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'nome', t: 'varchar(50)', nn: true, note: 'super_admin, diretor, professor, secretaria, aluno, encarregado, ...' },
        { n: 'descricao', t: 'text' },
        { n: 'permissoes', t: 'jsonb', def: '[]' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'utilizador_papel', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'utilizador_id', t: 'uuid', nn: true, fk: 'identity.utilizador' },
        { n: 'papel_id', t: 'uuid', nn: true, fk: 'identity.papel' },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'escopo', t: 'varchar(255)', note: 'escola, turma, municipal, provincial, nacional' },
        { n: 'ativo', t: 'boolean', def: 'true' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'sessao_ativa', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'utilizador_id', t: 'uuid', nn: true, fk: 'identity.utilizador' },
        { n: 'token_hash', t: 'varchar(255)', nn: true, note: 'Hash SHA-256 do token JWT' },
        { n: 'ip', t: 'varchar(50)', nn: true },
        { n: 'user_agent', t: 'varchar(500)' },
        { n: 'criado_em', t: 'timestamptz', nn: true },
        { n: 'expira_em', t: 'timestamptz', nn: true },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'politica_password', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant', note: '1:1 com tenant' },
        { n: 'comprimento_min', t: 'integer', nn: true, def: '8' },
        { n: 'complexidade', t: 'varchar(50)', nn: true, def: 'media', note: 'baixa, media, alta' },
        { n: 'validade_dias', t: 'integer', nn: true, def: '90', note: 'Dias ate expirar. 0 = nunca' },
        { n: 'bloqueio_tentativas', t: 'integer', nn: true, def: '5', note: 'Tentativas antes de bloquear' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
    ]
  },
  {
    id: 'escolas',
    name: 'Escolas',
    desc: 'Gestao de escolas, anos lectivos, infraestruturas, licencas e configuracoes',
    color: 'escolas',
    tables: [
      { name: 'escola', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant', note: '1:1 com tenant' },
        { n: 'nome', t: 'varchar(255)', nn: true },
        { n: 'codigo_sige', t: 'varchar(50)', note: 'Codigo SIGE nacional' },
        { n: 'natureza', t: 'varchar(50)', def: 'publica', note: 'publica, privada, publico_privada' },
        { n: 'nivel_ensino', t: 'varchar(100)', def: 'primario' },
        { n: 'estatuto_legal', t: 'varchar(100)', note: 'Estatuto legal da instituicao' },
        { n: 'provincia', t: 'varchar(100)', nn: true },
        { n: 'municipio', t: 'varchar(100)', nn: true },
        { n: 'comuna', t: 'varchar(100)' },
        { n: 'endereco', t: 'text' },
        { n: 'telefone', t: 'varchar(30)' },
        { n: 'email', t: 'varchar(255)' },
        { n: 'coordenadas_gps', t: 'point', note: 'Latitude/Longitude GPS' },
        { n: 'ativa', t: 'boolean', def: 'true' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'ano_letivo', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'escola_id', t: 'uuid', nn: true, fk: 'escolas.escola' },
        { n: 'ano', t: 'integer', nn: true, note: 'Ex: 2026' },
        { n: 'designacao', t: 'varchar(50)', nn: true, note: 'Ex: 2026/2027' },
        { n: 'data_inicio', t: 'date', nn: true },
        { n: 'data_fim', t: 'date', nn: true },
        { n: 'ativo', t: 'boolean', def: 'false', note: 'Apenas 1 ativo por escola' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'infraestrutura', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'escola_id', t: 'uuid', nn: true, fk: 'escolas.escola' },
        { n: 'nome', t: 'varchar(255)', nn: true },
        { n: 'tipo', t: 'varchar(50)', def: 'sala', note: 'sala, laboratorio, biblioteca, refeitorio, quadra, administrativo' },
        { n: 'quantidade', t: 'integer', nn: true, def: '1', note: 'Numero de unidades deste tipo' },
        { n: 'capacidade', t: 'integer' },
        { n: 'estado', t: 'varchar(30)', def: 'bom', note: 'bom, degradado, inoperante' },
        { n: 'observacoes', t: 'text' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'configuracao_escola', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'escola_id', t: 'uuid', nn: true, fk: 'escolas.escola', note: '1:1 com escola' },
        { n: 'idioma', t: 'varchar(10)', nn: true, def: 'pt', note: 'pt, en, fr' },
        { n: 'moeda', t: 'varchar(10)', nn: true, def: 'AOA', note: 'ISO 4217: AOA, USD, EUR' },
        { n: 'num_periodos', t: 'integer', def: '3' },
        { n: 'nota_maxima', t: 'integer', def: '20' },
        { n: 'nota_minima_aprovacao', t: 'integer', def: '10' },
        { n: 'regras_nota', t: 'jsonb', def: '{}', note: 'Formulas, pesos, arredondamento' },
        { n: 'politica_falta', t: 'jsonb', def: '{}', note: 'Limite faltas, justificacao, consequencias' },
        { n: 'parametros_vocacional', t: 'jsonb', def: '{}', note: 'Config. do modulo vocacional por escola' },
        { n: 'configuracao_extra', t: 'jsonb', def: '{}' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'licenca', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'escola_id', t: 'uuid', nn: true, fk: 'escolas.escola', note: '1:1 com escola' },
        { n: 'modulos_ativos', t: 'jsonb', nn: true, def: '[]', note: 'Array de modulos: academico, financeiro, provas, vocacional, etc.' },
        { n: 'limite_utilizadores', t: 'integer', nn: true, def: '50', note: 'Maximo de utilizadores permitidos' },
        { n: 'validade', t: 'date', nn: true, note: 'Data de expiracao da licenca' },
        { n: 'estado', t: 'varchar(20)', nn: true, def: 'ativa', note: 'ativa, suspensa, expirada' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
    ]
  },
  {
    id: 'directory',
    name: 'Directory',
    desc: 'Pessoas, alunos, professores, encarregados, funcionarios e vinculos',
    color: 'directory',
    tables: [
      { name: 'pessoa', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'nome_completo', t: 'varchar(255)', nn: true },
        { n: 'bi_identificacao', t: 'varchar(50)', nn: true, note: 'BI / Cartao de Cidadao' },
        { n: 'dt_nascimento', t: 'date', nn: true },
        { n: 'sexo', t: 'varchar(1)', nn: true, note: 'M, F' },
        { n: 'nacionalidade', t: 'varchar(100)', def: 'Angolana' },
        { n: 'morada', t: 'text' },
        { n: 'telefone', t: 'varchar(30)' },
        { n: 'email', t: 'varchar(255)' },
        { n: 'foto_url', t: 'varchar(500)', note: 'Referencia S3' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'aluno', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'pessoa_id', t: 'uuid', nn: true, fk: 'directory.pessoa' },
        { n: 'n_processo', t: 'varchar(50)', nn: true, note: 'Numero de processo' },
        { n: 'ano_ingresso', t: 'integer', nn: true },
        { n: 'necessidades_especiais', t: 'boolean', def: 'false' },
        { n: 'status', t: 'varchar(20)', def: 'ativo', note: 'ativo, transferido, desistente, concluinte' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'professor', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'pessoa_id', t: 'uuid', nn: true, fk: 'directory.pessoa' },
        { n: 'codigo_funcional', t: 'varchar(50)', nn: true },
        { n: 'especialidade', t: 'varchar(100)', nn: true },
        { n: 'carga_horaria_semanal', t: 'integer', nn: true },
        { n: 'tipo_contrato', t: 'varchar(20)', def: 'contrato', note: 'efetivo, contrato, substituto' },
        { n: 'nivel_academico', t: 'varchar(100)' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'encarregado', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'pessoa_id', t: 'uuid', nn: true, fk: 'directory.pessoa' },
        { n: 'profissao', t: 'varchar(100)' },
        { n: 'escolaridade', t: 'varchar(50)' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'funcionario', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'pessoa_id', t: 'uuid', nn: true, fk: 'directory.pessoa' },
        { n: 'cargo', t: 'varchar(100)', nn: true },
        { n: 'departamento', t: 'varchar(100)', nn: true },
        { n: 'data_admissao', t: 'date', nn: true },
        { n: 'tipo_contrato', t: 'varchar(20)', def: 'contrato' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'vinculo_aluno_encarregado', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'aluno_id', t: 'uuid', nn: true, fk: 'directory.aluno' },
        { n: 'encarregado_id', t: 'uuid', nn: true, fk: 'directory.encarregado' },
        { n: 'tipo', t: 'varchar(20)', nn: true, note: 'pai, mae, tutor, outro' },
        { n: 'principal', t: 'boolean', def: 'false', note: 'Encarregado principal' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
    ]
  },
  {
    id: 'enrollment',
    name: 'Enrollment',
    desc: 'Matriculas, alocacao em turmas, transferencias e documentos',
    color: 'enrollment',
    tables: [
      { name: 'matricula', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'aluno_id', t: 'uuid', nn: true, fk: 'directory.aluno' },
        { n: 'ano_letivo_id', t: 'uuid', nn: true, fk: 'escolas.ano_letivo' },
        { n: 'classe', t: 'varchar(10)', nn: true },
        { n: 'turno', t: 'varchar(20)', def: 'matutino' },
        { n: 'estado', t: 'varchar(20)', def: 'pendente', note: 'pendente, aprovada, rejeitada, cancelada' },
        { n: 'data_pedido', t: 'date', nn: true },
        { n: 'data_aprovacao', t: 'date' },
        { n: 'observacoes', t: 'text' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'alocacao_turma', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'matricula_id', t: 'uuid', nn: true, fk: 'enrollment.matricula' },
        { n: 'turma_id', t: 'uuid', nn: true, fk: 'academico.turma' },
        { n: 'data_alocacao', t: 'date', nn: true },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'transferencia', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'aluno_id', t: 'uuid', nn: true, fk: 'directory.aluno' },
        { n: 'escola_origem_id', t: 'uuid', nn: true, fk: 'escolas.escola' },
        { n: 'escola_destino_id', t: 'uuid', nn: true, fk: 'escolas.escola' },
        { n: 'data_pedido', t: 'date', nn: true },
        { n: 'estado', t: 'varchar(20)', def: 'pendente' },
        { n: 'motivo', t: 'text', nn: true },
        { n: 'documentos_url', t: 'jsonb', note: 'Array de URLs S3' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'documento_matricula', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'matricula_id', t: 'uuid', nn: true, fk: 'enrollment.matricula' },
        { n: 'tipo', t: 'varchar(50)', nn: true, note: 'cartao_cidadao, atestado_vacinacao, foto, etc.' },
        { n: 'url', t: 'varchar(500)', nn: true },
        { n: 'verificado', t: 'boolean', def: 'false' },
        { n: 'uploaded_at', t: 'timestamptz', nn: true },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
    ]
  },
  {
    id: 'academico',
    name: 'Academico',
    desc: 'Curriculos, disciplinas, turmas, horarios, diarios de classe e presencas',
    color: 'academico',
    tables: [
      { name: 'curriculo', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'nivel', t: 'varchar(50)', nn: true },
        { n: 'classe', t: 'varchar(10)', nn: true },
        { n: 'ano_letivo_id', t: 'uuid', nn: true, fk: 'escolas.ano_letivo' },
        { n: 'carga_horaria_total', t: 'integer', nn: true },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'disciplina', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'nome', t: 'varchar(255)', nn: true },
        { n: 'codigo', t: 'varchar(50)', nn: true },
        { n: 'curriculo_id', t: 'uuid', nn: true, fk: 'academico.curriculo' },
        { n: 'carga_horaria_semanal', t: 'integer', nn: true },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'turma', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'nome', t: 'varchar(50)', nn: true },
        { n: 'classe', t: 'varchar(10)', nn: true },
        { n: 'turno', t: 'varchar(20)', nn: true },
        { n: 'ano_letivo_id', t: 'uuid', nn: true, fk: 'escolas.ano_letivo' },
        { n: 'capacidade_max', t: 'integer', nn: true },
        { n: 'professor_regente_id', t: 'uuid', nn: true, fk: 'directory.professor' },
        { n: 'sala', t: 'varchar(100)' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'horario_aula', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'turma_id', t: 'uuid', nn: true, fk: 'academico.turma' },
        { n: 'disciplina_id', t: 'uuid', nn: true, fk: 'academico.disciplina' },
        { n: 'professor_id', t: 'uuid', nn: true, fk: 'directory.professor' },
        { n: 'dia_semana', t: 'varchar(10)', nn: true },
        { n: 'hora_inicio', t: 'time', nn: true },
        { n: 'hora_fim', t: 'time', nn: true },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'diario_classe', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'turma_id', t: 'uuid', nn: true, fk: 'academico.turma' },
        { n: 'disciplina_id', t: 'uuid', nn: true, fk: 'academico.disciplina' },
        { n: 'professor_id', t: 'uuid', nn: true, fk: 'directory.professor' },
        { n: 'data_aula', t: 'date', nn: true },
        { n: 'conteudo', t: 'text', nn: true },
        { n: 'sumario', t: 'text', nn: true },
        { n: 'observacoes', t: 'text' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'presenca_diario', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'diario_id', t: 'uuid', nn: true, fk: 'academico.diario_classe' },
        { n: 'aluno_id', t: 'uuid', nn: true, fk: 'directory.aluno' },
        { n: 'presente', t: 'boolean', nn: true },
        { n: 'justificativa', t: 'text' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
    ]
  },
  {
    id: 'avaliacoes',
    name: 'Avaliacoes',
    desc: 'Avaliacoes, notas, faltas, regras de media e boletins',
    color: 'avaliacoes',
    tables: [
      { name: 'avaliacao', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'turma_id', t: 'uuid', nn: true, fk: 'academico.turma' },
        { n: 'disciplina_id', t: 'uuid', nn: true, fk: 'academico.disciplina' },
        { n: 'tipo', t: 'varchar(20)', nn: true, note: 'teste, trabalho, exame, oral' },
        { n: 'periodo', t: 'integer', nn: true },
        { n: 'data', t: 'date', nn: true },
        { n: 'peso', t: 'float', nn: true },
        { n: 'nota_maxima', t: 'integer', nn: true },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'nota', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'avaliacao_id', t: 'uuid', nn: true, fk: 'avaliacoes.avaliacao' },
        { n: 'aluno_id', t: 'uuid', nn: true, fk: 'directory.aluno' },
        { n: 'valor', t: 'decimal', nn: true },
        { n: 'observacoes', t: 'text' },
        { n: 'lancado_por', t: 'uuid', nn: true, fk: 'directory.professor' },
        { n: 'lancado_em', t: 'timestamptz', nn: true },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'falta', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'aluno_id', t: 'uuid', nn: true, fk: 'directory.aluno' },
        { n: 'turma_id', t: 'uuid', nn: true, fk: 'academico.turma' },
        { n: 'disciplina_id', t: 'uuid', nn: true, fk: 'academico.disciplina' },
        { n: 'data', t: 'date', nn: true },
        { n: 'tipo', t: 'varchar(20)', nn: true, note: 'justificada, injustificada' },
        { n: 'justificativa', t: 'text' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'regra_media', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'nivel', t: 'varchar(50)', nn: true },
        { n: 'disciplina_id', t: 'uuid', fk: 'academico.disciplina', note: 'NULL = todas' },
        { n: 'formula', t: 'varchar(500)', nn: true },
        { n: 'minimo_aprovacao', t: 'integer', nn: true },
        { n: 'politica_recuperacao', t: 'text' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'boletim', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'aluno_id', t: 'uuid', nn: true, fk: 'directory.aluno' },
        { n: 'ano_letivo_id', t: 'uuid', nn: true, fk: 'escolas.ano_letivo' },
        { n: 'periodo', t: 'integer', nn: true },
        { n: 'gerado_em', t: 'timestamptz', nn: true },
        { n: 'url_pdf', t: 'varchar(500)', nn: true },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
    ]
  },
  {
    id: 'financeiro',
    name: 'Financeiro',
    desc: 'Planos de pagamento, faturas, pagamentos e bolsas de estudo',
    color: 'financeiro',
    tables: [
      { name: 'plano_pagamento', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'nome', t: 'varchar(100)', nn: true },
        { n: 'periodicidade', t: 'varchar(20)', nn: true },
        { n: 'valor_base', t: 'decimal', nn: true },
        { n: 'data_vencimento_dia', t: 'integer', nn: true },
        { n: 'politica_multa', t: 'decimal' },
        { n: 'politica_juros', t: 'decimal' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'fatura', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'aluno_id', t: 'uuid', nn: true, fk: 'directory.aluno' },
        { n: 'plano_id', t: 'uuid', nn: true, fk: 'financeiro.plano_pagamento' },
        { n: 'competencia', t: 'varchar(10)', nn: true },
        { n: 'valor_total', t: 'decimal', nn: true },
        { n: 'estado', t: 'varchar(20)', def: 'aberto' },
        { n: 'vencimento', t: 'date', nn: true },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'item_fatura', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'fatura_id', t: 'uuid', nn: true, fk: 'financeiro.fatura' },
        { n: 'descricao', t: 'varchar(255)', nn: true },
        { n: 'quantidade', t: 'integer', def: '1' },
        { n: 'valor_unitario', t: 'decimal', nn: true },
        { n: 'desconto', t: 'decimal' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'pagamento', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'fatura_id', t: 'uuid', nn: true, fk: 'financeiro.fatura' },
        { n: 'data', t: 'date', nn: true },
        { n: 'valor', t: 'decimal', nn: true },
        { n: 'canal', t: 'varchar(30)', nn: true, note: 'caixa, multicaixa_express, bai_directo, outro' },
        { n: 'nsu_transacao', t: 'varchar(50)', note: 'Referencia da transaccao' },
        { n: 'comprovativo_url', t: 'varchar(500)' },
        { n: 'registado_por', t: 'uuid', nn: true, fk: 'identity.utilizador' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'bolsa', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'aluno_id', t: 'uuid', nn: true, fk: 'directory.aluno' },
        { n: 'tipo', t: 'varchar(20)', nn: true, note: 'percentual, valor' },
        { n: 'valor', t: 'decimal', nn: true },
        { n: 'vigencia_inicio', t: 'date', nn: true },
        { n: 'vigencia_fim', t: 'date', nn: true },
        { n: 'criterio', t: 'text' },
        { n: 'aprovado_por', t: 'uuid', nn: true, fk: 'identity.utilizador' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
    ]
  },
  {
    id: 'provas',
    name: 'Provas',
    desc: 'Concursos, provas digitais, questoes, respostas e rankings',
    color: 'provas',
    tables: [
      { name: 'concurso', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'nome', t: 'varchar(255)', nn: true },
        { n: 'organizador', t: 'varchar(20)', nn: true, note: 'ANEP, PIC, outro' },
        { n: 'data_inicio', t: 'date', nn: true },
        { n: 'data_fim', t: 'date', nn: true },
        { n: 'nivel_minimo', t: 'varchar(50)', nn: true },
        { n: 'nivel_maximo', t: 'varchar(50)', nn: true },
        { n: 'estado', t: 'varchar(30)', def: 'planejamento' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'inscricao_concurso', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'concurso_id', t: 'uuid', nn: true, fk: 'provas.concurso' },
        { n: 'aluno_id', t: 'uuid', nn: true, fk: 'directory.aluno' },
        { n: 'escola_id', t: 'uuid', nn: true, fk: 'escolas.escola' },
        { n: 'data', t: 'date', nn: true },
        { n: 'estado', t: 'varchar(20)', def: 'inscrito' },
        { n: 'nota_final', t: 'decimal' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'prova_digital', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'concurso_id', t: 'uuid', nn: true, fk: 'provas.concurso' },
        { n: 'turma_id', t: 'uuid', fk: 'academico.turma' },
        { n: 'data_aplicacao', t: 'date', nn: true },
        { n: 'duracao_minutos', t: 'integer', nn: true },
        { n: 'estado', t: 'varchar(20)', def: 'nao_iniciada' },
        { n: 'chave_antifraude', t: 'varchar(100)', nn: true },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'questao', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'prova_id', t: 'uuid', nn: true, fk: 'provas.prova_digital' },
        { n: 'enunciado', t: 'text', nn: true },
        { n: 'tipo', t: 'varchar(20)', nn: true, note: 'escolha_multipla, dissertativa, verdadeiro_falso' },
        { n: 'opcoes', t: 'jsonb' },
        { n: 'resposta_correta', t: 'varchar(255)' },
        { n: 'pontuacao', t: 'integer', nn: true },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'resposta_aluno', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'prova_id', t: 'uuid', nn: true, fk: 'provas.prova_digital' },
        { n: 'aluno_id', t: 'uuid', nn: true, fk: 'directory.aluno' },
        { n: 'questao_id', t: 'uuid', nn: true, fk: 'provas.questao' },
        { n: 'resposta', t: 'text', nn: true },
        { n: 'pontuacao_obtida', t: 'integer' },
        { n: 'tempo_resposta', t: 'integer', nn: true, note: 'Segundos' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'ranking_concurso', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'concurso_id', t: 'uuid', nn: true, fk: 'provas.concurso' },
        { n: 'aluno_id', t: 'uuid', nn: true, fk: 'directory.aluno' },
        { n: 'escola_id', t: 'uuid', nn: true, fk: 'escolas.escola' },
        { n: 'posicao_escola', t: 'integer', nn: true },
        { n: 'posicao_municipal', t: 'integer', nn: true },
        { n: 'posicao_nacional', t: 'integer', nn: true },
        { n: 'pontuacao', t: 'decimal', nn: true },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
    ]
  },
  {
    id: 'vocacional',
    name: 'Vocacional',
    desc: 'Questionarios vocacionais, perfis, recomendacoes e relatorios',
    color: 'vocacional',
    tables: [
      { name: 'questionario_vocacional', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'nome', t: 'varchar(255)', nn: true },
        { n: 'versao', t: 'integer', def: '1' },
        { n: 'questoes', t: 'jsonb', nn: true },
        { n: 'ativo', t: 'boolean', def: 'true' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'resposta_vocacional', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'questionario_id', t: 'uuid', nn: true, fk: 'vocacional.questionario_vocacional' },
        { n: 'aluno_id', t: 'uuid', nn: true, fk: 'directory.aluno' },
        { n: 'respostas', t: 'jsonb', nn: true },
        { n: 'completado_em', t: 'timestamptz', nn: true },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'perfil_vocacional', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'aluno_id', t: 'uuid', nn: true, fk: 'directory.aluno' },
        { n: 'areas_interesse', t: 'jsonb', nn: true },
        { n: 'aptidoes', t: 'jsonb', nn: true },
        { n: 'tipo_personalidade', t: 'varchar(50)', nn: true },
        { n: 'completado_em', t: 'timestamptz', nn: true },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'recomendacao_curso', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'perfil_id', t: 'uuid', nn: true, fk: 'vocacional.perfil_vocacional' },
        { n: 'area', t: 'varchar(100)', nn: true },
        { n: 'curso', t: 'varchar(255)', nn: true },
        { n: 'instituicao_sugerida', t: 'varchar(255)' },
        { n: 'descricao', t: 'text' },
        { n: 'compatibilidade_pct', t: 'integer', nn: true },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'relatorio_vocacional', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'aluno_id', t: 'uuid', nn: true, fk: 'directory.aluno' },
        { n: 'perfil_id', t: 'uuid', nn: true, fk: 'vocacional.perfil_vocacional' },
        { n: 'gerado_em', t: 'timestamptz', nn: true },
        { n: 'url_pdf', t: 'varchar(500)', nn: true },
        { n: 'partilhado_com', t: 'jsonb' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
    ]
  },
  {
    id: 'relatorios',
    name: 'Relatorios',
    desc: 'Templates de relatorios, execucoes, paineis e auditoria',
    color: 'relatorios',
    tables: [
      { name: 'template_relatorio', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'nome', t: 'varchar(255)', nn: true },
        { n: 'tipo', t: 'varchar(20)', nn: true, note: 'SIGE, INE, MED, interno' },
        { n: 'parametros', t: 'jsonb', nn: true },
        { n: 'query_base', t: 'text', nn: true },
        { n: 'formato', t: 'varchar(10)', nn: true, note: 'xlsx, pdf, json, csv' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'execucao_relatorio', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'template_id', t: 'uuid', nn: true, fk: 'relatorios.template_relatorio' },
        { n: 'solicitado_por', t: 'uuid', nn: true, fk: 'identity.utilizador' },
        { n: 'parametros_usados', t: 'jsonb', nn: true },
        { n: 'estado', t: 'varchar(20)', def: 'pendente' },
        { n: 'url_output', t: 'varchar(500)' },
        { n: 'gerado_em', t: 'timestamptz' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'painel', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'nivel', t: 'varchar(20)', nn: true, note: 'escola, municipal, provincial, nacional' },
        { n: 'widgets', t: 'jsonb', nn: true },
        { n: 'configuracao', t: 'jsonb' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'registo_auditoria', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'utilizador_id', t: 'uuid', fk: 'identity.utilizador' },
        { n: 'acao', t: 'varchar(100)', nn: true, note: 'CREATE, UPDATE, DELETE, EXPORT' },
        { n: 'entidade', t: 'varchar(100)', nn: true },
        { n: 'entidade_id', t: 'uuid', nn: true },
        { n: 'dados_antes', t: 'jsonb' },
        { n: 'dados_depois', t: 'jsonb' },
        { n: 'timestamp', t: 'timestamptz', nn: true },
        { n: 'ip', t: 'varchar(50)' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
    ]
  },
  {
    id: 'estoque',
    name: 'Estoque',
    desc: 'Gestao de inventario: uniformes, livros, materiais e alertas de reposicao',
    color: 'estoque',
    tables: [
      { name: 'item_estoque', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'tipo', t: 'varchar(30)', nn: true, note: 'uniforme, livro, material_pedagogico' },
        { n: 'nome', t: 'varchar(255)', nn: true },
        { n: 'descricao', t: 'text' },
        { n: 'quantidade_total', t: 'integer', nn: true },
        { n: 'quantidade_disponivel', t: 'integer', nn: true },
        { n: 'unidade', t: 'varchar(50)', nn: true },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'atribuicao_item', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'item_id', t: 'uuid', nn: true, fk: 'estoque.item_estoque' },
        { n: 'aluno_id', t: 'uuid', nn: true, fk: 'directory.aluno' },
        { n: 'quantidade', t: 'integer', nn: true },
        { n: 'data_atribuicao', t: 'date', nn: true },
        { n: 'estado', t: 'varchar(20)', def: 'ativo' },
        { n: 'custo', t: 'decimal' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'movimento_estoque', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'item_id', t: 'uuid', nn: true, fk: 'estoque.item_estoque' },
        { n: 'tipo', t: 'varchar(20)', nn: true, note: 'entrada, saida, devolucao, perda' },
        { n: 'quantidade', t: 'integer', nn: true },
        { n: 'data', t: 'date', nn: true },
        { n: 'motivo', t: 'text', nn: true },
        { n: 'registado_por', t: 'uuid', nn: true, fk: 'identity.utilizador' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'alerta_reposicao', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'item_id', t: 'uuid', nn: true, fk: 'estoque.item_estoque' },
        { n: 'nivel_minimo', t: 'integer', nn: true },
        { n: 'ativo', t: 'boolean', def: 'true' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
    ]
  },
  {
    id: 'alimentacao',
    name: 'Alimentacao',
    desc: 'Cardapios, consumo de refeicoes, subsidios e fornecedores',
    color: 'alimentacao',
    tables: [
      { name: 'cardapio', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'data', t: 'date', nn: true },
        { n: 'turno', t: 'varchar(20)', nn: true },
        { n: 'descricao', t: 'text', nn: true },
        { n: 'custo_unitario', t: 'decimal', nn: true },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'consumo_refeicao', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'cardapio_id', t: 'uuid', nn: true, fk: 'alimentacao.cardapio' },
        { n: 'aluno_id', t: 'uuid', nn: true, fk: 'directory.aluno' },
        { n: 'presente', t: 'boolean', nn: true },
        { n: 'subsidiado', t: 'boolean', def: 'false' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'subsidio_alimentacao', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'aluno_id', t: 'uuid', nn: true, fk: 'directory.aluno' },
        { n: 'tipo', t: 'varchar(20)', nn: true, note: 'total, parcial' },
        { n: 'vigencia_inicio', t: 'date', nn: true },
        { n: 'vigencia_fim', t: 'date', nn: true },
        { n: 'aprovado_por', t: 'uuid', nn: true, fk: 'identity.utilizador' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'fornecedor', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'nome', t: 'varchar(255)', nn: true },
        { n: 'nif', t: 'varchar(20)', nn: true },
        { n: 'contacto', t: 'varchar(255)', nn: true },
        { n: 'contrato_url', t: 'varchar(500)' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
    ]
  },
  {
    id: 'integracoes',
    name: 'Integracoes',
    desc: 'Adaptadores para sistemas externos (SIUGEP, INE, Multicaixa, BAI Directo)',
    color: 'integracoes',
    tables: [
      { name: 'adaptador_integracao', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'nome', t: 'varchar(255)', nn: true },
        { n: 'tipo', t: 'varchar(30)', nn: true, note: 'SIUGEP, INE, GEPE, ANEP, Multicaixa, BAI_Directo' },
        { n: 'endpoint', t: 'varchar(500)', nn: true },
        { n: 'autenticacao', t: 'varchar(50)', nn: true, note: 'apikey, oauth2, hmac' },
        { n: 'estado', t: 'varchar(20)', def: 'ativo' },
        { n: 'ultima_sincronizacao', t: 'timestamptz' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'log_integracao', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'adaptador_id', t: 'uuid', nn: true, fk: 'integracoes.adaptador_integracao' },
        { n: 'timestamp', t: 'timestamptz', nn: true },
        { n: 'tipo', t: 'varchar(20)', nn: true, note: 'request, response, erro' },
        { n: 'payload', t: 'text', nn: true },
        { n: 'status_code', t: 'integer' },
        { n: 'latencia_ms', t: 'integer' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'fila_mensagem', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'adaptador_id', t: 'uuid', nn: true, fk: 'integracoes.adaptador_integracao' },
        { n: 'payload', t: 'jsonb', nn: true },
        { n: 'estado', t: 'varchar(20)', def: 'pendente' },
        { n: 'tentativas', t: 'integer', def: '0' },
        { n: 'proximo_retry', t: 'timestamptz' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
    ]
  },
  {
    id: 'sync',
    name: 'Sync',
    desc: 'Sincronizacao offline-first: sessoes, deltas locais e resolucao de conflitos',
    color: 'sync',
    tables: [
      { name: 'sessao_sync', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'local_id', t: 'varchar(100)', nn: true, note: 'Identificador do dispositivo' },
        { n: 'ultima_sync_bem_sucedida', t: 'timestamptz' },
        { n: 'estado', t: 'varchar(20)', def: 'pendente' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'delta_local', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'sessao_sync_id', t: 'uuid', nn: true, fk: 'sync.sessao_sync' },
        { n: 'entidade', t: 'varchar(100)', nn: true },
        { n: 'entidade_id', t: 'uuid', nn: true },
        { n: 'operacao', t: 'varchar(10)', nn: true, note: 'INSERT, UPDATE, DELETE' },
        { n: 'dados', t: 'jsonb', nn: true },
        { n: 'timestamp_local', t: 'timestamptz', nn: true },
        { n: 'sincronizado', t: 'boolean', def: 'false' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'conflito_dados', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'entidade', t: 'varchar(100)', nn: true },
        { n: 'entidade_id', t: 'uuid', nn: true },
        { n: 'valor_local', t: 'jsonb', nn: true },
        { n: 'valor_nuvem', t: 'jsonb', nn: true },
        { n: 'resolucao', t: 'varchar(20)', nn: true, note: 'LWW, manual_user, manual_admin' },
        { n: 'resolvido_por', t: 'uuid', fk: 'identity.utilizador' },
        { n: 'resolvido_em', t: 'timestamptz' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
    ]
  },
  {
    id: 'notifications',
    name: 'Notifications',
    desc: 'Notificacoes multi-canal (email, SMS, push, in-app) com templates e fila',
    color: 'notifications',
    tables: [
      { name: 'notificacao', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'tipo', t: 'varchar(20)', nn: true, note: 'email, sms, push_web, in_app' },
        { n: 'destinatario', t: 'varchar(255)', nn: true },
        { n: 'utilizador_id', t: 'uuid', fk: 'identity.utilizador' },
        { n: 'assunto', t: 'varchar(255)' },
        { n: 'corpo', t: 'text', nn: true },
        { n: 'estado', t: 'varchar(20)', def: 'pendente' },
        { n: 'tentativas', t: 'integer', def: '0' },
        { n: 'proxima_tentativa', t: 'timestamptz' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'template_notificacao', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'nome', t: 'varchar(100)', nn: true },
        { n: 'tipo', t: 'varchar(20)', nn: true },
        { n: 'assunto', t: 'varchar(255)' },
        { n: 'corpo', t: 'text', nn: true },
        { n: 'ativo', t: 'boolean', def: 'true' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
      { name: 'fila_notificacao', cols: [
        { n: 'id', t: 'uuid', pk: true },
        { n: 'tenant_id', t: 'uuid', nn: true, fk: 'identity.tenant' },
        { n: 'notificacao_id', t: 'uuid', nn: true, fk: 'notifications.notificacao' },
        { n: 'estado', t: 'varchar(20)', def: 'pendente' },
        { n: 'tentativas', t: 'integer', def: '0' },
        { n: 'proximo_retry', t: 'timestamptz' },
        { n: 'created_at', t: 'timestamptz', nn: true },
        { n: 'updated_at', t: 'timestamptz', nn: true },
        { n: 'deleted_at', t: 'timestamptz' },
      ]},
    ]
  },
];

// ── Computed cross-domain dependencies ──
function computeDeps() {
  const deps = {};
  DOMAINS.forEach(d => { deps[d.id] = new Set(); });

  DOMAINS.forEach(domain => {
    domain.tables.forEach(table => {
      table.cols.forEach(col => {
        if (col.fk) {
          const targetSchema = col.fk.split('.')[0];
          if (targetSchema !== domain.id) {
            deps[domain.id].add(targetSchema);
          }
        }
      });
    });
  });

  // Convert sets to arrays
  Object.keys(deps).forEach(k => { deps[k] = [...deps[k]]; });
  return deps;
}

function computeDependents(deps) {
  const dependents = {};
  DOMAINS.forEach(d => { dependents[d.id] = []; });
  Object.entries(deps).forEach(([src, targets]) => {
    targets.forEach(t => {
      if (!dependents[t].includes(src)) dependents[t].push(src);
    });
  });
  return dependents;
}

// ── State ──
let activeDomain = null;
let activeTable = null;
const deps = computeDeps();
const dependents = computeDependents(deps);

// ── Render ──
function init() {
  renderStats();
  renderLegend();
  renderGrid();
  bindSearch();
}

function renderStats() {
  const totalTables = DOMAINS.reduce((s, d) => s + d.tables.length, 0);
  const totalCols = DOMAINS.reduce((s, d) => s + d.tables.reduce((s2, t) => s2 + t.cols.length, 0), 0);
  const totalRefs = DOMAINS.reduce((s, d) =>
    s + d.tables.reduce((s2, t) =>
      s2 + t.cols.filter(c => c.fk).length, 0), 0);

  document.getElementById('stat-schemas').textContent = DOMAINS.length;
  document.getElementById('stat-tables').textContent = totalTables;
  document.getElementById('stat-cols').textContent = totalCols;
  document.getElementById('stat-refs').textContent = totalRefs;
}

function renderLegend() {
  const el = document.getElementById('legend');
  el.innerHTML = DOMAINS.map(d => `
    <span class="legend-item" data-domain="${d.id}"
      style="background: var(--c-${d.color}-bg); color: var(--c-${d.color}); border: 1px solid var(--c-${d.color}-border);"
      onclick="selectDomain('${d.id}')">
      ${d.name}
    </span>
  `).join('');
}

function renderGrid() {
  const grid = document.getElementById('grid');
  grid.innerHTML = DOMAINS.map(d => {
    const tableRows = d.tables.map(t => `
      <div class="table-item" data-table="${d.id}.${t.name}" onclick="event.stopPropagation(); showTableDetail('${d.id}', '${t.name}')">
        <span class="icon" style="background: var(--c-${d.color})"></span>
        <span class="name">${t.name}</span>
        <span class="cols">${t.cols.length} cols</span>
      </div>
    `).join('');

    return `
      <div class="domain-card" id="card-${d.id}" data-domain="${d.id}" onclick="selectDomain('${d.id}')">
        <div class="card-header" style="background: var(--c-${d.color}-bg); border-bottom: 2px solid var(--c-${d.color});">
          <h3 style="color: var(--c-${d.color})">${d.name}</h3>
          <span class="badge" style="background: var(--c-${d.color}); color: white;">${d.tables.length} tabelas</span>
        </div>
        <div class="card-body">${tableRows}</div>
      </div>
    `;
  }).join('');
}

function selectDomain(id) {
  if (activeDomain === id) {
    clearSelection();
    return;
  }

  activeDomain = id;
  activeTable = null;
  const domain = DOMAINS.find(d => d.id === id);
  const related = new Set([id, ...deps[id], ...dependents[id]]);

  // Update cards
  document.querySelectorAll('.domain-card').forEach(card => {
    const cid = card.dataset.domain;
    card.classList.remove('active', 'dimmed', 'highlighted');
    if (cid === id) {
      card.classList.add('active');
      card.style.borderColor = `var(--c-${domain.color})`;
    } else if (related.has(cid)) {
      card.classList.add('highlighted');
      const rel = DOMAINS.find(d => d.id === cid);
      card.style.borderColor = `var(--c-${rel.color})`;
    } else {
      card.classList.add('dimmed');
      card.style.borderColor = '';
    }
  });

  // Show detail panel
  showDomainDetail(domain);
}

function clearSelection() {
  activeDomain = null;
  activeTable = null;
  document.querySelectorAll('.domain-card').forEach(card => {
    card.classList.remove('active', 'dimmed', 'highlighted');
    card.style.borderColor = '';
  });
  document.getElementById('detail-panel').classList.remove('visible');
}

function showDomainDetail(domain) {
  const panel = document.getElementById('detail-panel');
  const depsArr = deps[domain.id];
  const depsOfArr = dependents[domain.id];

  const tablesHtml = domain.tables.map(t => `
    <div class="detail-table" style="cursor:pointer" onclick="showTableDetail('${domain.id}', '${t.name}')">
      <span class="dot" style="background: var(--c-${domain.color})"></span>
      <span>${t.name}</span>
      <span style="margin-left:auto; font-size:11px; color:var(--text-secondary)">${t.cols.length} cols</span>
    </div>
  `).join('');

  const depsHtml = depsArr.length ? depsArr.map(did => {
    const d = DOMAINS.find(x => x.id === did);
    return `<span class="dep-item" style="background:var(--c-${d.color}-bg); color:var(--c-${d.color}); border:1px solid var(--c-${d.color}-border)" onclick="selectDomain('${did}')">${d.name}</span>`;
  }).join('') : '<span style="font-size:12px; color:var(--text-secondary)">Nenhuma</span>';

  const depsOfHtml = depsOfArr.length ? depsOfArr.map(did => {
    const d = DOMAINS.find(x => x.id === did);
    return `<span class="dep-item" style="background:var(--c-${d.color}-bg); color:var(--c-${d.color}); border:1px solid var(--c-${d.color}-border)" onclick="selectDomain('${did}')">${d.name}</span>`;
  }).join('') : '<span style="font-size:12px; color:var(--text-secondary)">Nenhuma</span>';

  panel.innerHTML = `
    <div class="detail-content" style="position:relative">
      <button class="detail-close" onclick="clearSelection()">&times;</button>
      <div class="detail-header" style="background: var(--c-${domain.color}-bg); border-left: 4px solid var(--c-${domain.color});">
        <h2 style="color: var(--c-${domain.color})">${domain.name}</h2>
        <p>${domain.desc}</p>
      </div>
      <div class="detail-section">
        <h4>Tabelas (${domain.tables.length})</h4>
        ${tablesHtml}
      </div>
      <div class="detail-section">
        <h4>Depende de</h4>
        <div style="display:flex; flex-wrap:wrap; gap:4px">${depsHtml}</div>
      </div>
      <div class="detail-section">
        <h4>Dependentes</h4>
        <div style="display:flex; flex-wrap:wrap; gap:4px">${depsOfHtml}</div>
      </div>
    </div>
  `;
  panel.classList.add('visible');
}

function showTableDetail(domainId, tableName) {
  const domain = DOMAINS.find(d => d.id === domainId);
  const table = domain.tables.find(t => t.name === tableName);
  const panel = document.getElementById('detail-panel');

  const colsHtml = table.cols.map(c => {
    let badges = '';
    if (c.pk) badges += '<span class="col-pk">PK</span>';
    if (c.fk) badges += `<span class="col-fk">FK</span>`;
    let noteHtml = '';
    if (c.note) noteHtml = `<span class="col-note">${c.note}</span>`;
    if (c.fk) noteHtml += `<span class="col-note">-> ${c.fk}</span>`;

    return `
      <div>
        <div class="col-row">
          ${badges}
          <span>${c.n}</span>
          <span class="col-type">${c.t}${c.nn ? ' NOT NULL' : ''}</span>
        </div>
        ${noteHtml}
      </div>
    `;
  }).join('');

  const fkCols = table.cols.filter(c => c.fk);
  const refsHtml = fkCols.length ? fkCols.map(c => {
    const targetSchema = c.fk.split('.')[0];
    const td = DOMAINS.find(d => d.id === targetSchema);
    if (!td) return '';
    return `
      <div style="font-size:12px; padding:4px 0; font-family:monospace">
        <span style="color:var(--c-${domain.color})">${c.n}</span>
        <span style="color:var(--text-secondary)"> -> </span>
        <span style="color:var(--c-${td.color}); cursor:pointer" onclick="selectDomain('${targetSchema}')">${c.fk}</span>
      </div>
    `;
  }).join('') : '<span style="font-size:12px; color:var(--text-secondary)">Nenhuma FK externa</span>';

  panel.innerHTML = `
    <div class="detail-content" style="position:relative">
      <button class="detail-close" onclick="clearSelection()">&times;</button>
      <div class="detail-header" style="background: var(--c-${domain.color}-bg); border-left: 4px solid var(--c-${domain.color});">
        <h2 style="color: var(--c-${domain.color})">${domain.id}.${table.name}</h2>
        <p>${table.cols.length} colunas &middot; ${fkCols.length} foreign keys</p>
      </div>
      <div class="detail-section">
        <h4>Colunas</h4>
        <div class="col-list">${colsHtml}</div>
      </div>
      <div class="detail-section">
        <h4>Referencias</h4>
        ${refsHtml}
      </div>
      <div class="detail-section" style="text-align:center">
        <span class="dep-item" style="background:var(--c-${domain.color}-bg); color:var(--c-${domain.color}); border:1px solid var(--c-${domain.color}-border); cursor:pointer" onclick="selectDomain('${domain.id}')">
          Voltar ao dominio ${domain.name}
        </span>
      </div>
    </div>
  `;
  panel.classList.add('visible');
}

function bindSearch() {
  const input = document.getElementById('search');
  input.addEventListener('input', () => {
    const q = input.value.toLowerCase().trim();

    if (!q) {
      document.querySelectorAll('.domain-card').forEach(c => {
        c.classList.remove('hidden');
        c.querySelectorAll('.table-item').forEach(t => t.classList.remove('match'));
      });
      return;
    }

    DOMAINS.forEach(domain => {
      const card = document.getElementById(`card-${domain.id}`);
      const nameMatch = domain.id.includes(q) || domain.name.toLowerCase().includes(q);
      let hasTableMatch = false;

      card.querySelectorAll('.table-item').forEach(item => {
        const tName = item.dataset.table.split('.')[1];
        if (tName.includes(q)) {
          item.classList.add('match');
          hasTableMatch = true;
        } else {
          item.classList.remove('match');
        }
      });

      if (nameMatch || hasTableMatch) {
        card.classList.remove('hidden');
      } else {
        card.classList.add('hidden');
      }
    });
  });
}

document.addEventListener('DOMContentLoaded', init);