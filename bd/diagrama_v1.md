Project SIENA {
  database_type: "PostgreSQL"
  Note: '''
  Modelo relacional SIENA em DBML para dbdiagram.io
  Regras de negócio complexas foram mantidas fora do diagrama.
  '''
}

//////////////////////////////////////////////////////
// 01 — identity
//////////////////////////////////////////////////////

Table identity.tenant {
  id uuid [pk]
  nome varchar(255) [not null, note: 'Nome da escola/organização']
  estado varchar(20) [not null, default: 'ativo', note: 'ativo, suspensa, expirada']
  plano varchar(50) [not null, default: 'basico', note: 'basico, profissional, enterprise']
  licenca_validade timestamptz
  configuracao jsonb [default: '{}']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz
}

Table identity.utilizador {
  id uuid [pk]
  tenant_id uuid [not null]
  pessoa_id uuid [note: 'FK futura -> directory.pessoa.id']
  username varchar(100) [not null]
  senha_hash varchar(255) [not null, note: 'bcrypt (cost >= 12)']
  nome_completo varchar(255) [not null]
  email varchar(255)
  tipo varchar(30) [default: 'local', note: 'local, oidc']
  ativo boolean [default: true]
  mfa_segredo varchar(255) [note: 'TOTP secret']
  ultimo_login timestamptz
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    (tenant_id, username) [unique]
  }
}

Table identity.papel {
  id uuid [pk]
  nome varchar(50) [not null, unique, note: 'super_admin, diretor, professor, secretaria, aluno, encarregado, gestor_municipal, gestor_provincial, gestor_nacional, platform_admin']
  descricao text
  permissoes jsonb [default: '[]']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz
}

Table identity.utilizador_papel {
  id uuid [pk]
  utilizador_id uuid [not null]
  papel_id uuid [not null]
  tenant_id uuid [not null]
  escopo varchar(255) [note: 'escola, turma, municipal, provincial, nacional']
  ativo boolean [default: true]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    (utilizador_id, papel_id, escopo) [unique]
  }
}

//////////////////////////////////////////////////////
// 02 — escolas
//////////////////////////////////////////////////////

Table escolas.escola {
  id uuid [pk]
  tenant_id uuid [not null]
  nome varchar(255) [not null]
  codigo_sige varchar(50) [unique, note: 'Código SIGE nacional']
  tipo varchar(50) [default: 'publica', note: 'publica, privada, comparticipada']
  nivel_ensino varchar(100) [default: 'primario', note: 'primario, secundario_1ciclo, secundario_2ciclo, tecnico']
  provincia varchar(100) [not null]
  municipio varchar(100) [not null]
  comuna varchar(100)
  endereco text
  telefone varchar(30)
  email varchar(255)
  latitude float [note: 'GPS']
  longitude float [note: 'GPS']
  ativa boolean [default: true]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
  }
}

Table escolas.ano_letivo {
  id uuid [pk]
  tenant_id uuid [not null]
  escola_id uuid [not null]
  ano integer [not null, note: 'Ex: 2026']
  designacao varchar(50) [not null, note: 'Ex: 2026/2027']
  data_inicio date [not null]
  data_fim date [not null]
  ativo boolean [default: false, note: 'Apenas 1 ativo por escola']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    escola_id
    (escola_id, ano) [unique]
  }
}

Table escolas.infraestrutura {
  id uuid [pk]
  tenant_id uuid [not null]
  escola_id uuid [not null]
  nome varchar(255) [not null]
  tipo varchar(50) [default: 'sala_aula', note: 'sala_aula, laboratorio, biblioteca, quadra, cantina, administrativo']
  capacidade integer
  estado varchar(30) [default: 'operacional', note: 'operacional, em_reparacao, inoperacional']
  observacoes text
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    escola_id
  }
}

Table escolas.configuracao_escola {
  id uuid [pk]
  tenant_id uuid [not null]
  escola_id uuid [not null, unique, note: '1:1 com escola']
  num_periodos integer [default: 3]
  nota_maxima integer [default: 20]
  nota_minima_aprovacao integer [default: 10]
  configuracao_extra jsonb [default: '{}']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
  }
}

//////////////////////////////////////////////////////
// 03 — directory
//////////////////////////////////////////////////////

Table directory.pessoa {
  id uuid [pk]
  tenant_id uuid [not null]
  nome_completo varchar(255) [not null]
  bi_identificacao varchar(50) [not null, note: 'BI / Cartão de Cidadão']
  dt_nascimento date [not null]
  sexo varchar(1) [not null, note: 'M, F']
  nacionalidade varchar(100) [default: 'Angolana']
  morada text
  telefone varchar(30)
  email varchar(255)
  foto_url varchar(500) [note: 'Referência S3']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    (tenant_id, bi_identificacao) [unique]
  }
}

Table directory.aluno {
  id uuid [pk]
  tenant_id uuid [not null]
  pessoa_id uuid [not null]
  n_processo varchar(50) [not null, note: 'Número de processo']
  ano_ingresso integer [not null]
  necessidades_especiais boolean [default: false]
  status varchar(20) [default: 'ativo', note: 'ativo, transferido, desistente, concluinte']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    pessoa_id
    (tenant_id, n_processo) [unique]
  }
}

Table directory.professor {
  id uuid [pk]
  tenant_id uuid [not null]
  pessoa_id uuid [not null]
  codigo_funcional varchar(50) [not null]
  especialidade varchar(100) [not null, note: 'Área de formação']
  carga_horaria_semanal integer [not null]
  tipo_contrato varchar(20) [default: 'contrato', note: 'efetivo, contrato, substituto']
  nivel_academico varchar(100)
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    pessoa_id
  }
}

Table directory.encarregado {
  id uuid [pk]
  tenant_id uuid [not null]
  pessoa_id uuid [not null]
  profissao varchar(100)
  escolaridade varchar(50)
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    pessoa_id
  }
}

Table directory.funcionario {
  id uuid [pk]
  tenant_id uuid [not null]
  pessoa_id uuid [not null]
  cargo varchar(100) [not null]
  departamento varchar(100) [not null]
  data_admissao date [not null]
  tipo_contrato varchar(20) [default: 'contrato', note: 'efetivo, contrato']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    pessoa_id
  }
}

Table directory.vinculo_aluno_encarregado {
  id uuid [pk]
  tenant_id uuid [not null]
  aluno_id uuid [not null]
  encarregado_id uuid [not null]
  tipo varchar(20) [not null, note: 'pai, mae, tutor, outro']
  principal boolean [default: false, note: 'Encarregado principal']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    aluno_id
    encarregado_id
    (aluno_id, encarregado_id) [unique]
  }
}

//////////////////////////////////////////////////////
// 04 — enrollment
//////////////////////////////////////////////////////

Table enrollment.matricula {
  id uuid [pk]
  tenant_id uuid [not null]
  aluno_id uuid [not null]
  ano_letivo_id uuid [not null]
  classe varchar(10) [not null, note: '1.ª, 7.ª, 10.ª, etc.']
  turno varchar(20) [default: 'matutino', note: 'matutino, vespertino, nocturno']
  estado varchar(20) [default: 'pendente', note: 'pendente, aprovada, rejeitada, cancelada']
  data_pedido date [not null]
  data_aprovacao date
  observacoes text
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    aluno_id
    ano_letivo_id
    (tenant_id, aluno_id, ano_letivo_id) [unique]
  }
}

Table enrollment.alocacao_turma {
  id uuid [pk]
  tenant_id uuid [not null]
  matricula_id uuid [not null]
  turma_id uuid [not null]
  data_alocacao date [not null]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    matricula_id
    turma_id
  }
}

Table enrollment.transferencia {
  id uuid [pk]
  tenant_id uuid [not null]
  aluno_id uuid [not null]
  escola_origem_id uuid [not null]
  escola_destino_id uuid [not null]
  data_pedido date [not null]
  estado varchar(20) [default: 'pendente', note: 'pendente, aprovada, rejeitada, cancelada']
  motivo text [not null]
  documentos_url jsonb [note: 'Array de URLs S3']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    aluno_id
  }
}

Table enrollment.documento_matricula {
  id uuid [pk]
  tenant_id uuid [not null]
  matricula_id uuid [not null]
  tipo varchar(50) [not null, note: 'cartao_cidadao, atestado_vacinacao, foto, etc.']
  url varchar(500) [not null, note: 'Referência S3']
  verificado boolean [default: false]
  uploaded_at timestamptz [not null]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    matricula_id
  }
}

//////////////////////////////////////////////////////
// 05 — academico
//////////////////////////////////////////////////////

Table academico.curriculo {
  id uuid [pk]
  tenant_id uuid [not null]
  nivel varchar(50) [not null, note: 'primario, secundario_1ciclo, etc.']
  classe varchar(10) [not null]
  ano_letivo_id uuid [not null]
  carga_horaria_total integer [not null, note: 'Horas semanais']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    ano_letivo_id
  }
}

Table academico.disciplina {
  id uuid [pk]
  tenant_id uuid [not null]
  nome varchar(255) [not null]
  codigo varchar(50) [not null, note: 'Único por tenant']
  curriculo_id uuid [not null]
  carga_horaria_semanal integer [not null]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    curriculo_id
    (tenant_id, codigo) [unique]
  }
}

Table academico.turma {
  id uuid [pk]
  tenant_id uuid [not null]
  nome varchar(50) [not null, note: '7.ª-A, 10.ª-B, etc.']
  classe varchar(10) [not null]
  turno varchar(20) [not null, note: 'matutino, vespertino, nocturno']
  ano_letivo_id uuid [not null]
  capacidade_max integer [not null]
  professor_regente_id uuid [not null]
  sala varchar(100) [note: 'Sala/infraestrutura']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    ano_letivo_id
    professor_regente_id
  }
}

Table academico.horario_aula {
  id uuid [pk]
  tenant_id uuid [not null]
  turma_id uuid [not null]
  disciplina_id uuid [not null]
  professor_id uuid [not null]
  dia_semana varchar(10) [not null, note: 'segunda, terca, quarta, quinta, sexta, sabado']
  hora_inicio time [not null]
  hora_fim time [not null]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    turma_id
    disciplina_id
    professor_id
  }
}

Table academico.diario_classe {
  id uuid [pk]
  tenant_id uuid [not null]
  turma_id uuid [not null]
  disciplina_id uuid [not null]
  professor_id uuid [not null]
  data_aula date [not null]
  conteudo text [not null, note: 'Conteúdo leccionado']
  sumario text [not null, note: 'Sumário da aula']
  observacoes text
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    turma_id
    disciplina_id
    professor_id
  }
}

Table academico.presenca_diario {
  id uuid [pk]
  tenant_id uuid [not null]
  diario_id uuid [not null]
  aluno_id uuid [not null]
  presente boolean [not null]
  justificativa text
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    diario_id
    aluno_id
  }
}

//////////////////////////////////////////////////////
// 06 — avaliacoes
//////////////////////////////////////////////////////

Table avaliacoes.avaliacao {
  id uuid [pk]
  tenant_id uuid [not null]
  turma_id uuid [not null]
  disciplina_id uuid [not null]
  tipo varchar(20) [not null, note: 'teste, trabalho, exame, oral']
  periodo integer [not null, note: '1, 2 ou 3']
  data date [not null]
  peso float [not null, note: 'Peso na média final']
  nota_maxima integer [not null]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    turma_id
    disciplina_id
  }
}

Table avaliacoes.nota {
  id uuid [pk]
  tenant_id uuid [not null]
  avaliacao_id uuid [not null]
  aluno_id uuid [not null]
  valor decimal [not null]
  observacoes text
  lancado_por uuid [not null, note: 'Professor que lançou']
  lancado_em timestamptz [not null]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    avaliacao_id
    aluno_id
    (avaliacao_id, aluno_id) [unique]
  }
}

Table avaliacoes.falta {
  id uuid [pk]
  tenant_id uuid [not null]
  aluno_id uuid [not null]
  turma_id uuid [not null]
  disciplina_id uuid [not null]
  data date [not null]
  tipo varchar(20) [not null, note: 'justificada, injustificada']
  justificativa text
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    aluno_id
    turma_id
    disciplina_id
  }
}

Table avaliacoes.regra_media {
  id uuid [pk]
  tenant_id uuid [not null]
  nivel varchar(50) [not null]
  disciplina_id uuid [note: 'NULL = todas']
  formula varchar(500) [not null, note: 'Fórmula de cálculo']
  minimo_aprovacao integer [not null]
  politica_recuperacao text
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    disciplina_id
  }
}

Table avaliacoes.boletim {
  id uuid [pk]
  tenant_id uuid [not null]
  aluno_id uuid [not null]
  ano_letivo_id uuid [not null]
  periodo integer [not null]
  gerado_em timestamptz [not null]
  url_pdf varchar(500) [not null, note: 'Referência S3']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    aluno_id
    ano_letivo_id
  }
}

//////////////////////////////////////////////////////
// 07 — financeiro
//////////////////////////////////////////////////////

Table financeiro.plano_pagamento {
  id uuid [pk]
  tenant_id uuid [not null]
  nome varchar(100) [not null]
  periodicidade varchar(20) [not null, note: 'mensal, trimestral, anual']
  valor_base decimal [not null]
  data_vencimento_dia integer [not null, note: 'Dia do mês']
  politica_multa decimal [note: '% multa']
  politica_juros decimal [note: '% juros']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
  }
}

Table financeiro.fatura {
  id uuid [pk]
  tenant_id uuid [not null]
  aluno_id uuid [not null]
  plano_id uuid [not null]
  competencia varchar(10) [not null, note: '2026-03']
  valor_total decimal [not null]
  estado varchar(20) [default: 'aberto', note: 'aberto, pago, vencido, estornado']
  vencimento date [not null]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    aluno_id
    (aluno_id, plano_id, competencia) [unique]
  }
}

Table financeiro.item_fatura {
  id uuid [pk]
  tenant_id uuid [not null]
  fatura_id uuid [not null]
  descricao varchar(255) [not null]
  quantidade integer [default: 1]
  valor_unitario decimal [not null]
  desconto decimal
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    fatura_id
  }
}

Table financeiro.pagamento {
  id uuid [pk]
  tenant_id uuid [not null]
  fatura_id uuid [not null]
  data date [not null]
  valor decimal [not null]
  canal varchar(30) [not null, note: 'caixa, multicaixa_express, bai_directo, outro']
  nsu_transacao varchar(50) [note: 'Referência da transacção']
  comprovativo_url varchar(500) [note: 'S3']
  registado_por uuid [not null]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    fatura_id
    nsu_transacao [unique]
  }
}

Table financeiro.bolsa {
  id uuid [pk]
  tenant_id uuid [not null]
  aluno_id uuid [not null]
  tipo varchar(20) [not null, note: 'percentual, valor']
  valor decimal [not null, note: '% ou valor absoluto']
  vigencia_inicio date [not null]
  vigencia_fim date [not null]
  criterio text
  aprovado_por uuid [not null]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    aluno_id
  }
}

//////////////////////////////////////////////////////
// 08 — provas
//////////////////////////////////////////////////////

Table provas.concurso {
  id uuid [pk]
  tenant_id uuid [not null]
  nome varchar(255) [not null]
  organizador varchar(20) [not null, note: 'ANEP, PIC, outro']
  data_inicio date [not null]
  data_fim date [not null]
  nivel_minimo varchar(50) [not null]
  nivel_maximo varchar(50) [not null]
  estado varchar(30) [default: 'planejamento', note: 'planejamento, aberto, fechado, resultados_publicados']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
  }
}

Table provas.inscricao_concurso {
  id uuid [pk]
  tenant_id uuid [not null]
  concurso_id uuid [not null]
  aluno_id uuid [not null]
  escola_id uuid [not null]
  data date [not null]
  estado varchar(20) [default: 'inscrito', note: 'inscrito, participou, desistiu']
  nota_final decimal
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    concurso_id
    aluno_id
    escola_id
    (concurso_id, aluno_id) [unique]
  }
}

Table provas.prova_digital {
  id uuid [pk]
  tenant_id uuid [not null]
  concurso_id uuid [not null]
  turma_id uuid [note: 'Se prova de sala']
  data_aplicacao date [not null]
  duracao_minutos integer [not null]
  estado varchar(20) [default: 'nao_iniciada', note: 'nao_iniciada, em_progresso, finalizada']
  chave_antifraude varchar(100) [not null, note: 'Chave de sessão']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    concurso_id
    turma_id
  }
}

Table provas.questao {
  id uuid [pk]
  tenant_id uuid [not null]
  prova_id uuid [not null]
  enunciado text [not null]
  tipo varchar(20) [not null, note: 'escolha_multipla, dissertativa, verdadeiro_falso']
  opcoes jsonb [note: 'Para escolha múltipla']
  resposta_correta varchar(255) [note: 'Para correcção automática']
  pontuacao integer [not null]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    prova_id
  }
}

Table provas.resposta_aluno {
  id uuid [pk]
  tenant_id uuid [not null]
  prova_id uuid [not null]
  aluno_id uuid [not null]
  questao_id uuid [not null]
  resposta text [not null]
  pontuacao_obtida integer [note: 'Auto ou manual']
  tempo_resposta integer [not null, note: 'Segundos']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    prova_id
    aluno_id
    questao_id
    (prova_id, aluno_id, questao_id) [unique]
  }
}

Table provas.ranking_concurso {
  id uuid [pk]
  tenant_id uuid [not null]
  concurso_id uuid [not null]
  aluno_id uuid [not null]
  escola_id uuid [not null]
  posicao_escola integer [not null]
  posicao_municipal integer [not null]
  posicao_nacional integer [not null]
  pontuacao decimal [not null]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    concurso_id
    aluno_id
    escola_id
  }
}

//////////////////////////////////////////////////////
// 09 — vocacional
//////////////////////////////////////////////////////

Table vocacional.questionario_vocacional {
  id uuid [pk]
  tenant_id uuid [not null]
  nome varchar(255) [not null]
  versao integer [default: 1]
  questoes jsonb [not null, note: 'Array de objectos questão']
  ativo boolean [default: true]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
  }
}

Table vocacional.resposta_vocacional {
  id uuid [pk]
  tenant_id uuid [not null]
  questionario_id uuid [not null]
  aluno_id uuid [not null]
  respostas jsonb [not null, note: 'Respostas por ID de questão']
  completado_em timestamptz [not null]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    questionario_id
    aluno_id
  }
}

Table vocacional.perfil_vocacional {
  id uuid [pk]
  tenant_id uuid [not null]
  aluno_id uuid [not null]
  areas_interesse jsonb [not null]
  aptidoes jsonb [not null]
  tipo_personalidade varchar(50) [not null]
  completado_em timestamptz [not null]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    aluno_id
  }
}

Table vocacional.recomendacao_curso {
  id uuid [pk]
  tenant_id uuid [not null]
  perfil_id uuid [not null]
  area varchar(100) [not null]
  curso varchar(255) [not null]
  instituicao_sugerida varchar(255)
  descricao text
  compatibilidade_pct integer [not null, note: '% de compatibilidade']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    perfil_id
  }
}

Table vocacional.relatorio_vocacional {
  id uuid [pk]
  tenant_id uuid [not null]
  aluno_id uuid [not null]
  perfil_id uuid [not null]
  gerado_em timestamptz [not null]
  url_pdf varchar(500) [not null, note: 'S3']
  partilhado_com jsonb [note: 'IDs com permissão de ver']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    aluno_id
    perfil_id
  }
}

//////////////////////////////////////////////////////
// 10 — relatorios
//////////////////////////////////////////////////////

Table relatorios.template_relatorio {
  id uuid [pk]
  tenant_id uuid [not null]
  nome varchar(255) [not null]
  tipo varchar(20) [not null, note: 'SIGE, INE, MED, interno']
  parametros jsonb [not null, note: 'Parâmetros configuráveis']
  query_base text [not null, note: 'Lógica de extracção']
  formato varchar(10) [not null, note: 'xlsx, pdf, json, csv']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
  }
}

Table relatorios.execucao_relatorio {
  id uuid [pk]
  tenant_id uuid [not null]
  template_id uuid [not null]
  solicitado_por uuid [not null]
  parametros_usados jsonb [not null]
  estado varchar(20) [default: 'pendente', note: 'pendente, processando, concluido, erro']
  url_output varchar(500) [note: 'S3']
  gerado_em timestamptz
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    template_id
    solicitado_por
  }
}

Table relatorios.painel {
  id uuid [pk]
  tenant_id uuid [not null]
  nivel varchar(20) [not null, note: 'escola, municipal, provincial, nacional']
  widgets jsonb [not null, note: 'Configuração dos widgets']
  configuracao jsonb
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
  }
}

Table relatorios.registo_auditoria {
  id uuid [pk]
  tenant_id uuid [not null]
  utilizador_id uuid
  acao varchar(100) [not null, note: 'CREATE, UPDATE, DELETE, EXPORT']
  entidade varchar(100) [not null, note: 'Tabela afectada']
  entidade_id uuid [not null]
  dados_antes jsonb [note: 'Snapshot antes']
  dados_depois jsonb [note: 'Snapshot depois']
  timestamp timestamptz [not null]
  ip varchar(50)
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    utilizador_id
  }
}

//////////////////////////////////////////////////////
// 11 — estoque
//////////////////////////////////////////////////////

Table estoque.item_estoque {
  id uuid [pk]
  tenant_id uuid [not null]
  tipo varchar(30) [not null, note: 'uniforme, livro, material_pedagogico']
  nome varchar(255) [not null]
  descricao text
  quantidade_total integer [not null]
  quantidade_disponivel integer [not null]
  unidade varchar(50) [not null, note: 'unidade, caixa, lote']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
  }
}

Table estoque.atribuicao_item {
  id uuid [pk]
  tenant_id uuid [not null]
  item_id uuid [not null]
  aluno_id uuid [not null]
  quantidade integer [not null]
  data_atribuicao date [not null]
  estado varchar(20) [default: 'ativo', note: 'ativo, devolvido, perdido']
  custo decimal
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    item_id
    aluno_id
  }
}

Table estoque.movimento_estoque {
  id uuid [pk]
  tenant_id uuid [not null]
  item_id uuid [not null]
  tipo varchar(20) [not null, note: 'entrada, saida, devolucao, perda']
  quantidade integer [not null]
  data date [not null]
  motivo text [not null]
  registado_por uuid [not null]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    item_id
    registado_por
  }
}

Table estoque.alerta_reposicao {
  id uuid [pk]
  tenant_id uuid [not null]
  item_id uuid [not null]
  nivel_minimo integer [not null]
  ativo boolean [default: true]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    item_id
  }
}

//////////////////////////////////////////////////////
// 12 — alimentacao
//////////////////////////////////////////////////////

Table alimentacao.cardapio {
  id uuid [pk]
  tenant_id uuid [not null]
  data date [not null]
  turno varchar(20) [not null, note: 'matutino, vespertino, nocturno']
  descricao text [not null]
  custo_unitario decimal [not null]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
  }
}

Table alimentacao.consumo_refeicao {
  id uuid [pk]
  tenant_id uuid [not null]
  cardapio_id uuid [not null]
  aluno_id uuid [not null]
  presente boolean [not null]
  subsidiado boolean [default: false]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    cardapio_id
    aluno_id
  }
}

Table alimentacao.subsidio_alimentacao {
  id uuid [pk]
  tenant_id uuid [not null]
  aluno_id uuid [not null]
  tipo varchar(20) [not null, note: 'total, parcial']
  vigencia_inicio date [not null]
  vigencia_fim date [not null]
  aprovado_por uuid [not null]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    aluno_id
    aprovado_por
  }
}

Table alimentacao.fornecedor {
  id uuid [pk]
  tenant_id uuid [not null]
  nome varchar(255) [not null]
  nif varchar(20) [not null]
  contacto varchar(255) [not null]
  contrato_url varchar(500) [note: 'S3']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    nif
  }
}

//////////////////////////////////////////////////////
// 13 — integracoes
//////////////////////////////////////////////////////

Table integracoes.adaptador_integracao {
  id uuid [pk]
  tenant_id uuid [not null]
  nome varchar(255) [not null]
  tipo varchar(30) [not null, note: 'SIUGEP, INE, GEPE, ANEP, Multicaixa, BAI_Directo']
  endpoint varchar(500) [not null, note: 'URL da API externa']
  autenticacao varchar(50) [not null, note: 'apikey, oauth2, hmac']
  estado varchar(20) [default: 'ativo', note: 'ativo, inativo, erro']
  ultima_sincronizacao timestamptz
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
  }
}

Table integracoes.log_integracao {
  id uuid [pk]
  tenant_id uuid [not null]
  adaptador_id uuid [not null]
  timestamp timestamptz [not null]
  tipo varchar(20) [not null, note: 'request, response, erro']
  payload text [not null, note: 'Sanitizado']
  status_code integer
  latencia_ms integer
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    adaptador_id
  }
}

Table integracoes.fila_mensagem {
  id uuid [pk]
  tenant_id uuid [not null]
  adaptador_id uuid [not null]
  payload jsonb [not null]
  estado varchar(20) [default: 'pendente', note: 'pendente, processado, erro, DLQ']
  tentativas integer [default: 0, note: 'Máx. 5']
  proximo_retry timestamptz [note: 'Backoff exponencial']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    adaptador_id
  }
}

//////////////////////////////////////////////////////
// 14 — sync
//////////////////////////////////////////////////////

Table sync.sessao_sync {
  id uuid [pk]
  tenant_id uuid [not null]
  local_id varchar(100) [not null, note: 'Identificador do dispositivo']
  ultima_sync_bem_sucedida timestamptz
  estado varchar(20) [default: 'pendente', note: 'sincronizado, pendente, conflito']
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    local_id
  }
}

Table sync.delta_local {
  id uuid [pk]
  tenant_id uuid [not null]
  sessao_sync_id uuid [not null]
  entidade varchar(100) [not null, note: 'Nome da tabela']
  entidade_id uuid [not null]
  operacao varchar(10) [not null, note: 'INSERT, UPDATE, DELETE']
  dados jsonb [not null]
  timestamp_local timestamptz [not null]
  sincronizado boolean [default: false]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    sessao_sync_id
  }
}

Table sync.conflito_dados {
  id uuid [pk]
  tenant_id uuid [not null]
  entidade varchar(100) [not null]
  entidade_id uuid [not null]
  valor_local jsonb [not null]
  valor_nuvem jsonb [not null]
  resolucao varchar(20) [not null, note: 'LWW, manual_user, manual_admin']
  resolvido_por uuid
  resolvido_em timestamptz
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    resolvido_por
  }
}

//////////////////////////////////////////////////////
// 15 — notifications
//////////////////////////////////////////////////////

Table notifications.notificacao {
  id uuid [pk]
  tenant_id uuid [not null]
  tipo varchar(20) [not null, note: 'email, sms, push_web, in_app']
  destinatario varchar(255) [not null, note: 'Email ou telefone']
  utilizador_id uuid
  assunto varchar(255)
  corpo text [not null]
  estado varchar(20) [default: 'pendente', note: 'pendente, enviado, falha']
  tentativas integer [default: 0]
  proxima_tentativa timestamptz
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    utilizador_id
  }
}

Table notifications.template_notificacao {
  id uuid [pk]
  tenant_id uuid [not null]
  nome varchar(100) [not null, note: 'falta_alerta, vencimento_fatura, etc.']
  tipo varchar(20) [not null, note: 'email, sms, push, in_app']
  assunto varchar(255)
  corpo text [not null, note: 'Template com placeholders']
  ativo boolean [default: true]
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
  }
}

Table notifications.fila_notificacao {
  id uuid [pk]
  tenant_id uuid [not null]
  notificacao_id uuid [not null]
  estado varchar(20) [default: 'pendente', note: 'pendente, processado, erro, DLQ']
  tentativas integer [default: 0]
  proximo_retry timestamptz
  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  Indexes {
    tenant_id
    notificacao_id
  }
}

//////////////////////////////////////////////////////
// REFS
//////////////////////////////////////////////////////

Ref: identity.utilizador.tenant_id > identity.tenant.id
Ref: identity.utilizador_papel.utilizador_id > identity.utilizador.id
Ref: identity.utilizador_papel.papel_id > identity.papel.id
Ref: identity.utilizador_papel.tenant_id > identity.tenant.id

Ref: escolas.escola.tenant_id > identity.tenant.id
Ref: escolas.ano_letivo.tenant_id > identity.tenant.id
Ref: escolas.ano_letivo.escola_id > escolas.escola.id
Ref: escolas.infraestrutura.tenant_id > identity.tenant.id
Ref: escolas.infraestrutura.escola_id > escolas.escola.id
Ref: escolas.configuracao_escola.tenant_id > identity.tenant.id
Ref: escolas.configuracao_escola.escola_id > escolas.escola.id

Ref: directory.pessoa.tenant_id > identity.tenant.id
Ref: directory.aluno.tenant_id > identity.tenant.id
Ref: directory.aluno.pessoa_id > directory.pessoa.id
Ref: directory.professor.tenant_id > identity.tenant.id
Ref: directory.professor.pessoa_id > directory.pessoa.id
Ref: directory.encarregado.tenant_id > identity.tenant.id
Ref: directory.encarregado.pessoa_id > directory.pessoa.id
Ref: directory.funcionario.tenant_id > identity.tenant.id
Ref: directory.funcionario.pessoa_id > directory.pessoa.id
Ref: directory.vinculo_aluno_encarregado.tenant_id > identity.tenant.id
Ref: directory.vinculo_aluno_encarregado.aluno_id > directory.aluno.id
Ref: directory.vinculo_aluno_encarregado.encarregado_id > directory.encarregado.id

Ref: enrollment.matricula.tenant_id > identity.tenant.id
Ref: enrollment.matricula.aluno_id > directory.aluno.id
Ref: enrollment.matricula.ano_letivo_id > escolas.ano_letivo.id
Ref: enrollment.alocacao_turma.tenant_id > identity.tenant.id
Ref: enrollment.alocacao_turma.matricula_id > enrollment.matricula.id
Ref: enrollment.alocacao_turma.turma_id > academico.turma.id
Ref: enrollment.transferencia.tenant_id > identity.tenant.id
Ref: enrollment.transferencia.aluno_id > directory.aluno.id
Ref: enrollment.transferencia.escola_origem_id > escolas.escola.id
Ref: enrollment.transferencia.escola_destino_id > escolas.escola.id
Ref: enrollment.documento_matricula.tenant_id > identity.tenant.id
Ref: enrollment.documento_matricula.matricula_id > enrollment.matricula.id

Ref: academico.curriculo.tenant_id > identity.tenant.id
Ref: academico.curriculo.ano_letivo_id > escolas.ano_letivo.id
Ref: academico.disciplina.tenant_id > identity.tenant.id
Ref: academico.disciplina.curriculo_id > academico.curriculo.id
Ref: academico.turma.tenant_id > identity.tenant.id
Ref: academico.turma.ano_letivo_id > escolas.ano_letivo.id
Ref: academico.turma.professor_regente_id > directory.professor.id
Ref: academico.horario_aula.tenant_id > identity.tenant.id
Ref: academico.horario_aula.turma_id > academico.turma.id
Ref: academico.horario_aula.disciplina_id > academico.disciplina.id
Ref: academico.horario_aula.professor_id > directory.professor.id
Ref: academico.diario_classe.tenant_id > identity.tenant.id
Ref: academico.diario_classe.turma_id > academico.turma.id
Ref: academico.diario_classe.disciplina_id > academico.disciplina.id
Ref: academico.diario_classe.professor_id > directory.professor.id
Ref: academico.presenca_diario.tenant_id > identity.tenant.id
Ref: academico.presenca_diario.diario_id > academico.diario_classe.id
Ref: academico.presenca_diario.aluno_id > directory.aluno.id

Ref: avaliacoes.avaliacao.tenant_id > identity.tenant.id
Ref: avaliacoes.avaliacao.turma_id > academico.turma.id
Ref: avaliacoes.avaliacao.disciplina_id > academico.disciplina.id
Ref: avaliacoes.nota.tenant_id > identity.tenant.id
Ref: avaliacoes.nota.avaliacao_id > avaliacoes.avaliacao.id
Ref: avaliacoes.nota.aluno_id > directory.aluno.id
Ref: avaliacoes.nota.lancado_por > directory.professor.id
Ref: avaliacoes.falta.tenant_id > identity.tenant.id
Ref: avaliacoes.falta.aluno_id > directory.aluno.id
Ref: avaliacoes.falta.turma_id > academico.turma.id
Ref: avaliacoes.falta.disciplina_id > academico.disciplina.id
Ref: avaliacoes.regra_media.tenant_id > identity.tenant.id
Ref: avaliacoes.regra_media.disciplina_id > academico.disciplina.id
Ref: avaliacoes.boletim.tenant_id > identity.tenant.id
Ref: avaliacoes.boletim.aluno_id > directory.aluno.id
Ref: avaliacoes.boletim.ano_letivo_id > escolas.ano_letivo.id

Ref: financeiro.plano_pagamento.tenant_id > identity.tenant.id
Ref: financeiro.fatura.tenant_id > identity.tenant.id
Ref: financeiro.fatura.aluno_id > directory.aluno.id
Ref: financeiro.fatura.plano_id > financeiro.plano_pagamento.id
Ref: financeiro.item_fatura.tenant_id > identity.tenant.id
Ref: financeiro.item_fatura.fatura_id > financeiro.fatura.id
Ref: financeiro.pagamento.tenant_id > identity.tenant.id
Ref: financeiro.pagamento.fatura_id > financeiro.fatura.id
Ref: financeiro.pagamento.registado_por > identity.utilizador.id
Ref: financeiro.bolsa.tenant_id > identity.tenant.id
Ref: financeiro.bolsa.aluno_id > directory.aluno.id
Ref: financeiro.bolsa.aprovado_por > identity.utilizador.id

Ref: provas.concurso.tenant_id > identity.tenant.id
Ref: provas.inscricao_concurso.tenant_id > identity.tenant.id
Ref: provas.inscricao_concurso.concurso_id > provas.concurso.id
Ref: provas.inscricao_concurso.aluno_id > directory.aluno.id
Ref: provas.inscricao_concurso.escola_id > escolas.escola.id
Ref: provas.prova_digital.tenant_id > identity.tenant.id
Ref: provas.prova_digital.concurso_id > provas.concurso.id
Ref: provas.prova_digital.turma_id > academico.turma.id
Ref: provas.questao.tenant_id > identity.tenant.id
Ref: provas.questao.prova_id > provas.prova_digital.id
Ref: provas.resposta_aluno.tenant_id > identity.tenant.id
Ref: provas.resposta_aluno.prova_id > provas.prova_digital.id
Ref: provas.resposta_aluno.aluno_id > directory.aluno.id
Ref: provas.resposta_aluno.questao_id > provas.questao.id
Ref: provas.ranking_concurso.tenant_id > identity.tenant.id
Ref: provas.ranking_concurso.concurso_id > provas.concurso.id
Ref: provas.ranking_concurso.aluno_id > directory.aluno.id
Ref: provas.ranking_concurso.escola_id > escolas.escola.id

Ref: vocacional.questionario_vocacional.tenant_id > identity.tenant.id
Ref: vocacional.resposta_vocacional.tenant_id > identity.tenant.id
Ref: vocacional.resposta_vocacional.questionario_id > vocacional.questionario_vocacional.id
Ref: vocacional.resposta_vocacional.aluno_id > directory.aluno.id
Ref: vocacional.perfil_vocacional.tenant_id > identity.tenant.id
Ref: vocacional.perfil_vocacional.aluno_id > directory.aluno.id
Ref: vocacional.recomendacao_curso.tenant_id > identity.tenant.id
Ref: vocacional.recomendacao_curso.perfil_id > vocacional.perfil_vocacional.id
Ref: vocacional.relatorio_vocacional.tenant_id > identity.tenant.id
Ref: vocacional.relatorio_vocacional.aluno_id > directory.aluno.id
Ref: vocacional.relatorio_vocacional.perfil_id > vocacional.perfil_vocacional.id

Ref: relatorios.template_relatorio.tenant_id > identity.tenant.id
Ref: relatorios.execucao_relatorio.tenant_id > identity.tenant.id
Ref: relatorios.execucao_relatorio.template_id > relatorios.template_relatorio.id
Ref: relatorios.execucao_relatorio.solicitado_por > identity.utilizador.id
Ref: relatorios.painel.tenant_id > identity.tenant.id
Ref: relatorios.registo_auditoria.tenant_id > identity.tenant.id
Ref: relatorios.registo_auditoria.utilizador_id > identity.utilizador.id

Ref: estoque.item_estoque.tenant_id > identity.tenant.id
Ref: estoque.atribuicao_item.tenant_id > identity.tenant.id
Ref: estoque.atribuicao_item.item_id > estoque.item_estoque.id
Ref: estoque.atribuicao_item.aluno_id > directory.aluno.id
Ref: estoque.movimento_estoque.tenant_id > identity.tenant.id
Ref: estoque.movimento_estoque.item_id > estoque.item_estoque.id
Ref: estoque.movimento_estoque.registado_por > identity.utilizador.id
Ref: estoque.alerta_reposicao.tenant_id > identity.tenant.id
Ref: estoque.alerta_reposicao.item_id > estoque.item_estoque.id

Ref: alimentacao.cardapio.tenant_id > identity.tenant.id
Ref: alimentacao.consumo_refeicao.tenant_id > identity.tenant.id
Ref: alimentacao.consumo_refeicao.cardapio_id > alimentacao.cardapio.id
Ref: alimentacao.consumo_refeicao.aluno_id > directory.aluno.id
Ref: alimentacao.subsidio_alimentacao.tenant_id > identity.tenant.id
Ref: alimentacao.subsidio_alimentacao.aluno_id > directory.aluno.id
Ref: alimentacao.subsidio_alimentacao.aprovado_por > identity.utilizador.id
Ref: alimentacao.fornecedor.tenant_id > identity.tenant.id

Ref: integracoes.adaptador_integracao.tenant_id > identity.tenant.id
Ref: integracoes.log_integracao.tenant_id > identity.tenant.id
Ref: integracoes.log_integracao.adaptador_id > integracoes.adaptador_integracao.id
Ref: integracoes.fila_mensagem.tenant_id > identity.tenant.id
Ref: integracoes.fila_mensagem.adaptador_id > integracoes.adaptador_integracao.id

Ref: sync.sessao_sync.tenant_id > identity.tenant.id
Ref: sync.delta_local.tenant_id > identity.tenant.id
Ref: sync.delta_local.sessao_sync_id > sync.sessao_sync.id
Ref: sync.conflito_dados.tenant_id > identity.tenant.id
Ref: sync.conflito_dados.resolvido_por > identity.utilizador.id

Ref: notifications.notificacao.tenant_id > identity.tenant.id
Ref: notifications.notificacao.utilizador_id > identity.utilizador.id
Ref: notifications.template_notificacao.tenant_id > identity.tenant.id
Ref: notifications.fila_notificacao.tenant_id > identity.tenant.id
Ref: notifications.fila_notificacao.notificacao_id > notifications.notificacao.id

Ref: identity.utilizador.pessoa_id > directory.pessoa.id