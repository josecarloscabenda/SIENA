|                                                                                                                            |
| -------------------------------------------------------------------------------------------------------------------------- |
| **SIENA**<br><br>Sistema de Integração Educacional Nacional de Angola<br><br>━━━━━━━━━━━━━━━━━━━━                          |
| **SN 2 — Requisitos Funcionais e Não-Funcionais**                                                                          |
| Versão 2.0  \|  Março 2026<br><br>_Baseado em microserviços por domínio  \|  Backend: Python/FastAPI  \|  Frontend: React_ |

**1. Documento de Visão**

**1.1 Contexto e Problema**

**Angola possui um sistema de gestão educacional fragmentado. Os principais problemas identificados são:**

- Dados escolares dispersos e sem integração nacional;
- Forte dependência de processos manuais e planilhas Excel;
- Baixa visibilidade dos indicadores educacionais a nível nacional e provincial;
- O circuito SIGE → planilhas ainda é necessário para consolidar o Anuário Educacional;
- O setor privado (ANEP) carece de plataforma confiável para provas e concursos;
- Ausência de solução nacional para exames vocacionais e orientação profissional;
- Sem ferramenta integrada para gestão de recursos (uniformes, manuais) e alimentação escolar.

  

**1.2 Objetivo**

**Disponibilizar um sistema unificado, escalável e seguro para gestão académica, administrativa e estatística de escolas (públicas e privadas), com portais por perfil, relatórios oficiais, concursos, vocacional e operação offline resiliente.**

  

**1.3 Proposta de Valor**

|   |   |
|---|---|
|**Unificação nacional**|Todos os dados educacionais centralizados e padronizados|
|**Eficiência operacional**|Menos papel, menos retrabalho, processos automatizados|
|**Transparência**|Famílias e órgãos gestores com acesso a dados confiáveis em tempo real|
|**Plataforma de provas**|Infraestrutura nacional para concursos ANEP/PIC com rankings|
|**Dados para políticas**|Indicadores confiáveis para o Anuário, MED e INE|
|**Escalabilidade**|Arquitetura que cresce desde uma escola até todo o país|

  

**1.4 Âmbito do Sistema**

**Incluído no sistema:**

- Gestão de Escolas (cadastro, infraestrutura, licenças);
- Gestão de Pessoas (alunos, professores, encarregados, funcionários);
- Matrículas (presencial e online);
- Académico (turmas, disciplinas, horários, diário de classe);
- Avaliações (notas, faltas, boletins);
- Financeiro (propinas, bolsas, pagamentos);
- Concursos e Provas (ANEP, PIC);
- Vocacional (questionários, perfis, recomendações);
- Relatórios (SIGE/INE/MED);
- Estoque (uniformes, livros);
- Alimentação Escolar;
- Identidade e Segurança (SSO, RBAC, MFA);
- Sincronização local ↔ nuvem (offline-first).

  

**Excluído do MVP (a considerar em versões futuras):**

- BI ministerial avançado com modelos preditivos;
- Gerador automático de horários (inicia manual/assistido);
- Integrações legadas complexas fora das listadas;
- Aplicação mobile completa (apenas versão web responsiva no MVP).

  

**1.5 Personas**

|   |   |
|---|---|
|**Aluno**|Consulta boletins, horários, faltas, resultados de concursos e perfil vocacional|
|**Encarregado**|Acompanha desempenho, paga propinas, recebe comunicados e resultados|
|**Professor**|Lança notas/faltas, gere diário de classe, aplica provas online|
|**Secretaria/Admin da Escola**|Gere matrículas, turmas, parâmetros anuais, finanças e estoque|
|**Diretor**|Visão global da escola, relatórios, indicadores, aprovação de processos|
|**Gestor Municipal/Provincial**|Painéis consolidados, exportações, auditoria regional|
|**Gestor Nacional (MED/INE)**|Dados nacionais, Anuário, políticas educacionais|
|**ANEP**|Gestão de concursos/provas nacionais e rankings|
|**Suporte Técnico**|Monitorização, auditoria, operações de sincronização|

  

**1.6 KPIs de Sucesso**

|   |   |
|---|---|
|**Adoção**|% escolas ativas; % professores a lançar notas; % alunos com vocacional concluído|
|**Uso**|Tempo médio de lançamento por turma; acessos mensais de encarregados|
|**Qualidade dos dados**|% registos completos e sem duplicidade; erros de sincronização < 0,1%/mês|
|**Performance**|p95 portais ≤ 3s; p95 admin ≤ 2s; relatórios ≤ 2 min; importações (50k linhas) ≤ 5 min|
|**Financeiro (escolas priv.)**|Redução de inadimplência; taxa de conciliação automática|

**2. Requisitos Funcionais**

**Cada requisito segue o formato: Âmbito • Entidades • Fluxos • Regras de Negócio • Relatórios**

**_Os módulos correspondem aos domínios de negócio da arquitetura modular. Cada módulo possui o seu próprio schema PostgreSQL e segue Clean Architecture internamente._**

  

  

|   |
|---|
|**RF-01**  **Gestão de Escolas**|

  

**Âmbito**

**Cadastro, configuração e gestão de instituições de ensino. Este módulo é a entidade base (tenant) de todo o sistema — separado da gestão de pessoas.**

  

**Entidades Principais**

- Escola: id, nome, provincia, municipio, commune, endereco, telefone, email, codigo_sige, natureza (pública/privada/público-privada), nivel_ensino, estatuto_legal, coordenadas_gps, created_at, updated_at
- Infraestrutura: id, escola_id, tipo (sala/laboratório/biblioteca/refeitório/quadra), quantidade, capacidade, estado (bom/degradado/inoperante)
- AnoLetivo: id, escola_id, ano, data_inicio, data_fim, ativo
- Licenca: id, escola_id, modulos_ativos[], limite_utilizadores, validade, estado (ativa/suspensa/expirada)
- ConfiguracaoEscola: id, escola_id, idioma, moeda, politica_falta, regras_nota, parametros_vocacional

  

**Fluxos Principais**

- Criação de escola pelo Super Admin da plataforma (com validação de unicidade por código SIGE);
- Edição de dados e infraestrutura pela secretaria/direção;
- Configuração de parâmetros anuais (ano letivo, regras académicas) no início de cada ano;
- Suspensão/reativação de escola por gestão da plataforma;
- Listagem e pesquisa de escolas por província, município e estatuto.

  

**Regras de Negócio**

- Cada escola é um tenant isolado — tenant_id obrigatório em todas as entidades do sistema;
- Uma escola só pode ter um AnoLetivo ativo por vez;
- A criação de escola só é permitida ao Super Admin (gestão da plataforma);
- O código SIGE deve ser único no sistema quando fornecido;
- A suspensão da licença bloqueia o acesso de todos os utilizadores da escola, exceto do Super Admin.

  

**Relatórios**

- Lista de escolas ativas por província/município;
- Relatório de infraestruturas por escola (para MED e INE);
- Escolas com licença prestes a expirar (alerta);
- Distribuição de escolas por natureza (pública/privada/público-privada).

  

  

|   |
|---|
|**RF-02**  **Gestão de Pessoas**|

  

**Âmbito**

**Cadastro central de todas as pessoas do sistema: alunos, encarregados, professores e funcionários. Módulo de diretório — não inclui escolas.**

  

**Entidades Principais**

- Pessoa: id, tenant_id, nome_completo, bi_identificacao, dt_nascimento, sexo, nacionalidade, morada, telefone, email, foto_url, created_at, updated_at
- Aluno: id, tenant_id, pessoa_id, n_processo, ano_ingresso, necessidades_especiais, status (ativo/transferido/desistente/concluinte)
- Encarregado: id, tenant_id, pessoa_id, profissao, escolaridade
- Professor: id, tenant_id, pessoa_id, codigo_funcional, especialidade, carga_horaria_semanal, tipo_contrato, nivel_academico
- Funcionario: id, tenant_id, pessoa_id, cargo, departamento, data_admissao, tipo_contrato
- Vinculo: id, tenant_id, aluno_id, encarregado_id, tipo (pai/mãe/tutor/outro), principal (boolean)
- UsuarioSistema: id, pessoa_id, tenant_id, username, senha_hash, tipo_usuario, ativo, ultimo_login

  

**Fluxos Principais**

- Cadastro de nova pessoa (com validação de BI duplicado por tenant);
- Associação de um aluno a um ou mais encarregados (com encarregado principal);
- Atribuição de papel/perfil ao utilizador (aluno, professor, secretaria, diretor, etc.);
- Importação em lote de alunos e professores via CSV com validação prévia;
- Pesquisa avançada por nome, BI, número de processo.

  

**Regras de Negócio**

- O BI deve ser único por tenant (escola) — alerta se duplicado;
- Um aluno deve ter pelo menos um encarregado principal associado;
- A criação de UsuarioSistema requer uma Pessoa previamente cadastrada;
- Passwords armazenadas com bcrypt (cost ≥ 12);
- Registo de auditoria em todas as operações de criação/edição/inativação.

  

**Relatórios**

- Total de alunos por escola, turno e género;
- Lista de professores por especialidade e tipo de contrato;
- Alunos com necessidades especiais por escola;
- Relatório de efetivo docente para o MED/GEPE.

  

  

|   |
|---|
|**RF-03**  **Matrículas**|

  

**Âmbito**

**Gestão completa do processo de matrícula: pedido, análise, aprovação/rejeição, alocação em turma e transferências.**

  

**Entidades Principais**

- Matricula: id, tenant_id, aluno_id, ano_letivo_id, classe, turno, estado (pendente/aprovada/rejeitada/cancelada), data_pedido, data_aprovacao, observacoes
- AlocacaoTurma: id, matricula_id, turma_id, data_alocacao
- Transferencia: id, aluno_id, escola_origem_id, escola_destino_id, data_pedido, estado, motivo, documentos_url[]
- DocumentoMatricula: id, matricula_id, tipo, url, verificado

  

**Fluxos Principais**

- Pedido de matrícula online (portal do encarregado) ou presencial (secretaria);
- Análise e aprovação/rejeição pela secretaria com justificação;
- Alocação automática ou manual em turma (respeitando vagas e turno);
- Processo de transferência entre escolas com rastreabilidade completa;
- Geração de comprovativo de matrícula em PDF.

  

**Regras de Negócio**

- Não é possível matricular o mesmo aluno duas vezes no mesmo ano letivo na mesma escola;
- A alocação em turma não pode exceder a capacidade máxima da turma;
- Uma transferência só pode ser iniciada com matrícula aprovada na escola de origem;
- Os documentos exigidos são configuráveis por escola (RF-01 — ConfiguracaoEscola);
- A rejeição de matrícula deve registar motivo obrigatório.

  

**Relatórios**

- Total de matrículas por classe, turno e estado;
- Taxa de aprovação de matrículas por período;
- Transferências por escola, município e motivo;
- Relatório oficial de efetivo escolar para o MED (compatível com SIGE).

  

  

|   |
|---|
|**RF-04**  **Módulo Académico**|

  

**Âmbito**

**Gestão do currículo, turmas, horários e diário de classe digital.**

  

**Entidades Principais**

- Curriculo: id, tenant_id, nivel, classe, ano_letivo_id, carga_horaria_total
- Disciplina: id, tenant_id, nome, codigo, curriculo_id, carga_horaria_semanal
- Turma: id, tenant_id, nome, classe, turno, ano_letivo_id, capacidade_max, professor_regente_id, sala
- HorarioAula: id, turma_id, disciplina_id, professor_id, dia_semana, hora_inicio, hora_fim
- DiarioClasse: id, turma_id, disciplina_id, data_aula, professor_id, conteudo, sumario, observacoes
- PresencaDiario: id, diario_id, aluno_id, presente (boolean), justificativa

  

**Fluxos Principais**

- Configuração do currículo por nível/classe no início do ano letivo;
- Criação de turmas com alocação de professor regente e sala;
- Geração de horário semanal com deteção de conflitos (professor/sala duplicados);
- Lançamento do diário de classe pelo professor (conteúdos lecionados e presenças);
- Publicação do horário para consulta pelos alunos e encarregados.

  

**Regras de Negócio**

- Um professor não pode ter duas aulas ao mesmo tempo (conflito de horário);
- Uma sala não pode ter duas turmas ao mesmo tempo;
- O diário de classe é obrigatório para cada aula lecionada;
- O lançamento no diário deve ser feito pelo professor da disciplina;
- Alterações ao horário devem notificar os utilizadores afetados.

  

**Relatórios**

- Horário semanal por turma/professor;
- Taxa de preenchimento do diário de classe por professor;
- Carga horária lecionada vs. prevista por disciplina;
- Distribuição de turmas por turno e classe.

  

  

|   |
|---|
|**RF-05**  **Avaliações, Notas e Faltas**|

  

**Âmbito**

**Registo e gestão de notas, faltas, cálculo de médias e geração de boletins escolares.**

  

**Entidades Principais**

- Avaliacao: id, tenant_id, turma_id, disciplina_id, tipo (teste/trabalho/exame/oral), periodo, data, peso, nota_maxima
- Nota: id, avaliacao_id, aluno_id, valor, observacoes, lancado_por, lancado_em
- Falta: id, tenant_id, aluno_id, turma_id, disciplina_id, data, tipo (justificada/injustificada), justificativa
- RegraMedia: id, tenant_id, nivel, disciplina_id, formula, minimo_aprovacao, politica_recuperacao
- Boletim: id, aluno_id, ano_letivo_id, periodo, gerado_em, url_pdf

  

**Fluxos Principais**

- Lançamento de notas por avaliação pelo professor responsável;
- Cálculo automático de médias segundo as regras configuradas (RF-01);
- Justificação de faltas pelo encarregado ou secretaria;
- Geração de boletim digital em PDF por período;
- Alerta automático ao encarregado quando o aluno excede o limite de faltas.

  

**Regras de Negócio**

- Notas devem estar no intervalo [0, nota_maxima] da avaliação;
- Uma nota só pode ser editada dentro do prazo configurado pela secretaria;
- O número máximo de faltas permitidas é configurável por escola e nível;
- Um aluno com faltas acima do limite perde o direito à avaliação (configurável);
- A geração do boletim só é possível com todas as notas do período lançadas.

  

**Relatórios**

- Boletim individual por aluno e período;
- Taxa de aprovação por disciplina, turma e classe;
- Indicadores de abandono e repetência;
- Ranking de alunos por desempenho (opt-in configurable by school);
- Relatório de faltas por aluno, turma e disciplina.

  

|   |
|---|
|**RF-06**  **Financeiro**|

  

**Âmbito**

**Gestão de propinas, taxas, bolsas, pagamentos e reconciliação financeira. Aplica-se principalmente a escolas privadas e público-privadas.**

  

**Entidades Principais**

- PlanoPagamento: id, tenant_id, nome, periodicidade (mensal/trimestral/anual), valor_base, data_vencimento_dia, politica_multa, politica_juros
- Fatura: id, tenant_id, aluno_id, plano_id, competencia, itens[], valor_total, estado (aberto/pago/vencido/estornado), vencimento
- Pagamento: id, fatura_id, data, valor, canal (caixa/gateway), nsu_transacao, comprovativo_url, registado_por
- Bolsa: id, tenant_id, aluno_id, tipo (percentual/valor), valor, vigencia_inicio, vigencia_fim, criterio, aprovado_por
- ItemFatura: id, fatura_id, descricao, quantidade, valor_unitario, desconto

  

**Fluxos Principais**

- Geração automática de faturas mensais/trimestrais por plano de pagamento;
- Registo de pagamento em caixa ou via gateway (Multicaixa Express);
- Aplicação automática de bolsas e descontos na faturação;
- Envio de alertas de vencimento para o encarregado (D-3, D0, D+7);
- Estorno de pagamento com justificação e registo de auditoria.

  

**Regras de Negócio**

- Uma fatura não pode ser emitida para um aluno sem matrícula ativa;
- Bolsas são aplicadas automaticamente na geração da fatura;
- Pagamentos não podem ser eliminados — apenas estornados;
- A conciliação financeira deve fechar o dia com soma de pagamentos igual ao caixa;
- Relatórios financeiros só são acessíveis pela direção e gestão provincial/nacional.

  

**Relatórios**

- Extrato financeiro por aluno (faturas, pagamentos, saldo devedor);
- Relatório mensal de receitas por escola;
- Taxa de inadimplência por período;
- Relatório de bolsas concedidas e impacto orçamental.

  

  

|   |
|---|
|**RF-07**  **Concursos e Provas (ANEP/PIC)**|

  

**Âmbito**

**Plataforma de provas digitais para concursos nacionais e internacionais, em parceria com a ANEP.**

  

**Entidades Principais**

- Concurso: id, nome, organizador (ANEP/PIC/outro), data_inicio, data_fim, nivel_minimo, nivel_maximo, estado
- InscricaoConcurso: id, concurso_id, aluno_id, escola_id, data, estado, nota_final
- ProvaDigital: id, concurso_id, turma_id, data_aplicacao, duracao_minutos, estado, chave_antifraude
- Questao: id, prova_id, enunciado, tipo (escolha_multipla/dissertativa), opcoes[], resposta_correta, pontuacao
- RespostaAluno: id, prova_id, aluno_id, questao_id, resposta, pontuacao_obtida, tempo_resposta
- RankingConcurso: id, concurso_id, aluno_id, escola_id, posicao_escola, posicao_municipal, posicao_nacional, pontuacao

  

**Fluxos Principais**

- Criação e configuração de concurso pela ANEP ou pela plataforma;
- Inscrição de alunos elegíveis pela secretaria da escola;
- Aplicação de prova digital com temporizador e mecanismo antifraude;
- Correção automática de questões de escolha múltipla;
- Geração de rankings por escola, município e nível nacional;
- Publicação de resultados e notificação a alunos e encarregados.

  

**Regras de Negócio**

- Um aluno só pode participar num concurso uma vez;
- A prova digital bloqueia cópia de texto e mudança de aba (antifraude básico);
- Rankings só são publicados após validação pela entidade organizadora;
- Os resultados individuais são visíveis apenas ao aluno e encarregado;
- Provas com questões dissertativas requerem correção manual pelo professor.

  

**Relatórios**

- Rankings nacionais, provinciais e por escola;
- Relatório de participação por escola e município;
- Desempenho médio por disciplina/tema;
- Histórico de concursos do aluno.

  

  

|   |
|---|
|**RF-08**  **Exames Vocacionais e Orientação**|

  

**Âmbito**

**Módulo de orientação profissional para alunos do ensino secundário (classes 9–12), com questionários, perfis e recomendações.**

  

**Entidades Principais**

- QuestionarioVocacional: id, tenant_id, nome, versao, questoes[], ativo
- RespostaVocacional: id, questionario_id, aluno_id, respostas{}, completado_em
- PerfilVocacional: id, aluno_id, areas_interesse[], aptidoes[], tipo_personalidade, completado_em
- RecomendacaoCurso: id, perfil_id, area, curso, instituicao_sugerida, descricao, compatibilidade_pct
- RelatorioVocacional: id, aluno_id, perfil_id, gerado_em, url_pdf, partilhado_com[]

  

**Fluxos Principais**

- Atribuição de questionário vocacional a turmas elegíveis (classes 9–12);
- Preenchimento do questionário pelo aluno (online ou offline com sincronização);
- Cálculo automático do perfil vocacional com base nas respostas;
- Geração de relatório personalizado em PDF;
- Partilha do relatório com encarregado, professor e diretor;
- Consolidação de indicadores vocacionais por escola/município/província.

  

**Regras de Negócio**

- O questionário vocacional só está disponível para alunos das classes 9–12;
- O relatório só é gerado após 100% do questionário preenchido;
- Os dados vocacionais são pessoais — acesso restrito ao aluno, encarregado e direção;
- O aluno pode refazer o questionário no máximo uma vez por ano letivo.

  

**Relatórios**

- Distribuição de perfis vocacionais por escola e município;
- Áreas de interesse mais escolhidas por região;
- Taxa de conclusão do questionário vocacional por turma/escola;
- Relatório vocacional individual (PDF partilhável).

  

|   |
|---|
|**RF-09**  **Relatórios e Governança**|

  

**Âmbito**

**Geração de relatórios oficiais para MED, INE, GEPE e órgãos locais, com painéis consolidados por nível administrativo.**

  

**Entidades Principais**

- TemplateRelatorio: id, nome, tipo (SIGE/INE/MED/interno), parametros[], query_base, formato (xlsx/pdf/json)
- ExecucaoRelatorio: id, template_id, solicitado_por, parametros_usados, estado, url_output, gerado_em
- Painel: id, tenant_id, nivel (escola/municipal/provincial/nacional), widgets[], configuracao
- RegistoAuditoria: id, tenant_id, utilizador_id, acao, entidade, entidade_id, dados_antes, dados_depois, timestamp, ip

  

**Fluxos Principais**

- Geração de relatórios oficiais (efetivo escolar, docentes, infraestruturas, indicadores);
- Exportação de dados no formato SIGE para compatibilidade com sistemas legados;
- Painéis consolidados por nível de acesso (escola / municipal / provincial / nacional);
- Registo automático de auditoria em todas as operações sensíveis;
- Agendamento de relatórios periódicos com entrega por e-mail.

  

**Regras de Negócio**

- Relatórios de dados nacionais só são acessíveis por perfis MED/INE;
- O registo de auditoria não pode ser eliminado nem editado;
- Os relatórios gerados devem ser reproduzíveis com os mesmos parâmetros;
- Exportações em formato SIGE devem passar por validação de esquema antes de entrega.

  

**Relatórios**

- Efetivo escolar nacional (alunos matriculados por classe, turno, género, natureza da escola);
- Indicadores de qualidade (aprovação, repetência, abandono) por escola/município/província;
- Relatório de docentes (total, por especialidade, por tipo de contrato);
- Anuário educacional (dados compatíveis com publicação do INE);
- Rankings de escolas por indicadores de desempenho (uso interno).

  

  

|   |
|---|
|**RF-10**  **Estoque e Recursos (Uniformes e Livros)**|

  

**Âmbito**

**Gestão de inventário de uniformes e livros escolares, atribuição a alunos e controlo de stock.**

  

**Entidades Principais**

- ItemEstoque: id, tenant_id, tipo (uniforme/livro), nome, descricao, quantidade_total, quantidade_disponivel, unidade
- AtribuicaoItem: id, item_id, aluno_id, quantidade, data_atribuicao, estado (ativo/devolvido/perdido), custo
- MovimentoEstoque: id, item_id, tipo (entrada/saída/devolução/perda), quantidade, data, motivo, registado_por
- AlertaReposicao: id, item_id, nivel_minimo, ativo

  

**Fluxos Principais**

- Registo de entradas de stock (fornecedores);
- Atribuição de uniformes/livros a alunos com registo de estado;
- Devolução e gestão de perdas com cobrança associada;
- Alerta automático quando o stock atinge o nível mínimo;
- Inventário periódico com reconciliação.

  

**Regras de Negócio**

- Não é possível atribuir mais itens do que o stock disponível;
- Perdas devem gerar uma cobrança no módulo financeiro (RF-06);
- O histórico de movimentos de stock não pode ser eliminado.

  

**Relatórios**

- Inventário atual por tipo de item;
- Itens atribuídos por aluno;
- Histórico de movimentos por item;
- Itens em falta ou abaixo do nível mínimo.

  

  

|   |
|---|
|**RF-11**  **Alimentação Escolar**|

  

**Âmbito**

**Planeamento e controlo de refeições escolares, subsídios e gestão de fornecedores.**

  

**Entidades Principais**

- Cardapio: id, tenant_id, data, turno, descricao, custo_unitario
- ConsumoRefeicao: id, cardapio_id, aluno_id, presente (boolean), subsidiado (boolean)
- SubsidioAlimentacao: id, tenant_id, aluno_id, tipo (total/parcial), vigencia_inicio, vigencia_fim, aprovado_por
- Fornecedor: id, tenant_id, nome, nif, contacto, contrato_url

  

**Fluxos Principais**

- Planeamento semanal/mensal do cardápio;
- Registo diário de presença nas refeições;
- Gestão de subsídios/isenções de alimentação com aprovação;
- Controlo de custos por fornecedor;
- Relatório de elegibilidade (alunos subsidiados).

  

**Regras de Negócio**

- O custo de refeições subsidiadas não é cobrado ao encarregado;
- Apenas alunos com matrícula ativa podem ser marcados como presentes;
- Os subsídios requerem aprovação pela direção da escola.

  

**Relatórios**

- Consumo diário/mensal de refeições por turno;
- Custo total de alimentação por mês;
- Lista de alunos subsidiados;
- Despesa por fornecedor.

  

  

|   |
|---|
|**RF-12**  **Integrações Externas**|

  

**Âmbito**

**Adaptadores de integração com sistemas governamentais e serviços externos.**

  

**Entidades Principais**

- AdaptadorIntegracao: id, nome, tipo (SIUGEP/INE/ANEP/Pagamento), endpoint, autenticacao, estado, ultima_sincronizacao
- LogIntegracao: id, adaptador_id, timestamp, tipo (request/response/erro), payload, status_code, latencia_ms
- FilaMensagem: id, adaptador_id, payload, estado (pendente/processado/erro/DLQ), tentativas, proximo_retry

  

**Fluxos Principais**

- Exportação de dados para o INE/GEPE no formato definido;
- Certificação de documentos via SIUGEP;
- Processamento de pagamentos via Multicaixa Express/BAI Directo;
- Envio de dados de concursos para a ANEP;
- Retry automático com backoff exponencial em caso de falha.

  

**Regras de Negócio**

- Todas as chamadas externas devem ser registadas no LogIntegracao;
- Mensagens com mais de 5 tentativas falhadas vão para a Dead Letter Queue (DLQ);
- Operações de pagamento são idempotentes (mesmo NSU não processa duas vezes);
- As credenciais de integração são armazenadas em cofre de segredos (não em BD).

  

**Relatórios**

- Taxa de sucesso das integrações por adaptador;
- Latência média e percentil 95 de chamadas externas;
- Mensagens em DLQ pendentes de intervenção manual.

  

  

|   |
|---|
|**RF-13**  **Identidade, Segurança e RBAC**|

  

**Âmbito**

**Gestão de autenticação, autorização e conformidade com proteção de dados.**

  

**Entidades Principais**

- Papel: id, nome (super_admin/platform_admin/diretor/secretaria/professor/encarregado/aluno), descricao, permissoes[]
- UtilizadorPapel: id, utilizador_id, papel_id, tenant_id, escopo (escola/turma/nacional), ativo
- SessaoAtiva: id, utilizador_id, token_hash, ip, user_agent, criado_em, expira_em
- PolíticaPassword: id, tenant_id, comprimento_min, complexidade, validade_dias, bloqueio_tentativas

  

**Fluxos Principais**

- Login único via SSO (Keycloak/OIDC);
- Emissão de tokens JWT com expiração configurável (access: 15min, refresh: 7 dias);
- MFA obrigatório para perfis administrativos (secretaria, diretor, gestores);
- Renovação automática de refresh token;
- Registo de auditoria de acessos, logins e operações sensíveis.

  

**Regras de Negócio**

- Passwords armazenadas apenas como hash bcrypt (cost ≥ 12);
- JWT deve incluir: sub, tenant_id, papel, scope, iat, exp;
- Após 5 tentativas falhadas de login, conta bloqueada por 15 minutos;
- Row-Level Security (RLS) ativo na nuvem para garantir isolamento entre tenants;
- Dados pessoais encriptados em repouso (AES-256) e em trânsito (TLS 1.3);
- Conformidade com a legislação angolana de proteção de dados pessoais.

  

**Relatórios**

- Utilizadores ativos por papel e tenant;
- Tentativas de login falhadas por IP (deteção de ataques);
- Auditoria de acessos sensíveis (relatórios nacionais, dados financeiros).

  

**3. Requisitos Não-Funcionais**

  

**3.1 Performance**

|   |   |   |
|---|---|---|
|**Requisito**|**Métrica**|**Estratégia**|
|Portais (web)|p95 ≤ 3 segundos|Cache Redis, CDN para assets estáticos|
|Admin / Secretaria|p95 ≤ 2 segundos|Query optimization, índices compostos, paginação|
|Geração de relatórios|≤ 2 minutos para relatórios padrão|Jobs assíncronos com notificação ao utilizador|
|Importação em lote|≤ 5 min para 50.000 linhas|Processamento em stream com validação progressiva|
|Sincronização offline|Delta sync ≤ 30 segundos|Outbox pattern + CDC, compressão de payload|

  

**3.2 Disponibilidade e Resiliência**

|   |   |   |
|---|---|---|
|**Requisito**|**Métrica**|**Estratégia**|
|Uptime (nuvem)|≥ 99,5% mensal|Multi-AZ, load balancer com health checks|
|Admin local (offline)|Funcional sem internet|SQLite local + agente de sync assíncrono|
|Recuperação de falha|RTO ≤ 4h, RPO ≤ 1h|Backups automáticos a cada hora, failover automático|
|Degradação graciosa|Funcionalidades críticas operacionais|Circuit breaker por serviço, cache de última leitura|

  

**3.3 Escalabilidade**

|   |   |   |
|---|---|---|
|**Requisito**|**Métrica**|**Estratégia**|
|Escolas|Suporte a 10.000+ tenants|Multi-tenant com isolamento por RLS|
|Utilizadores simultâneos|10.000+ sem degradação|Horizontal scaling da aplicação via réplicas; evolução para Kubernetes HPA quando a escala justificar|
|Dados históricos|10+ anos sem impacto na performance|Particionamento de tabelas por ano letivo|
|Expansão geográfica|Todas as 18 províncias|Infraestrutura cloud multi-região, sem redesign|

  

**3.4 Segurança**

|   |   |   |
|---|---|---|
|**Requisito**|**Métrica**|**Estratégia**|
|Autenticação|OIDC/OAuth2 + MFA admin|Keycloak / IdP local|
|Autorização|RBAC + RLS por tenant|Verificação em cada request pelo API Gateway|
|Encriptação|TLS 1.3 em trânsito, AES-256 em repouso|Certificados geridos automaticamente (Let's Encrypt)|
|Conformidade|Legislação angolana de dados pessoais|DPO nomeado, auditoria semestral|
|Vulnerabilidades|OWASP Top 10 mitigadas|SAST/DAST no CI/CD, pentests semestrais|

  

**3.5 Usabilidade**

|   |   |   |
|---|---|---|
|**Requisito**|**Métrica**|**Estratégia**|
|Aprendizagem|≤ 2 horas para tarefas básicas|UX simples, tours guiados no onboarding|
|Acessibilidade|WCAG 2.1 nível AA|Contraste, navegação por teclado, leitores de ecrã|
|Suporte mobile|Responsivo até 320px de largura|Design mobile-first, PWA instalável|
|Idiomas|Português (PT-AO) por defeito|i18n preparada para futura expansão|

  

**3.6 Manutenibilidade**

|   |   |   |
|---|---|---|
|**Requisito**|**Métrica**|**Estratégia**|
|Cobertura de testes|≥ 80% cobertura de código|Pytest (backend), Jest/Testing Library (frontend)|
|Documentação de API|OpenAPI 3.1 (Swagger UI)|Gerada automaticamente pelo FastAPI|
|Logs e observabilidade|Logs JSON estruturados|Prometheus + Grafana + OpenTelemetry|
|Versionamento de API|/api/v1, semver, feature flags|Nunca quebrar versão anterior sem período de deprecação|