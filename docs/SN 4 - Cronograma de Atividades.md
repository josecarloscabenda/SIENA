|                                                                                                                                |
| ------------------------------------------------------------------------------------------------------------------------------ |
| **SIENA**<br><br>Sistema de Integração Educacional Nacional de Angola<br><br>━━━━━━━━━━━━━━━━━━━━                              |
| **SN 4 — Cronograma de Atividades**                                                                                            |
| Versão 1.0  \|  Março 2026<br><br>_Plano de 6 meses: MVP (Mês 3) → Versão 1.0 (Mês 6)  \|  Baseado em metodologia Agile/Scrum_ |

**1. Resumo Executivo do Projeto**

|   |   |
|---|---|
|**Nome do Projeto**|SIENA — Sistema de Integração Educacional Nacional de Angola|
|**Patrocinador**|Ministério da Educação de Angola (MED)|
|**Metodologia**|Agile/Scrum — Sprints de 2 semanas|
|**Duração total**|6 meses (MVP em 3 meses, Versão 1.0 em 6 meses)|
|**Data de início (estimada)**|Abril 2026|
|**Data MVP (estimada)**|Junho 2026|
|**Data Versão 1.0 (estimada)**|Setembro 2026|
|**Equipa**|6 pessoas: 2 Backend (Python), 1 Frontend (React), 1 Mobile (React Native), 1 DevOps, 1 Analista/QA|
|**Sprints**|12 sprints de 2 semanas ao longo de 6 meses|
|**Ambiente alvo**|Docker Compose (dev) + servidor staging/produção + Admin local offline|

  

**2. Fases do Projeto**

|   |   |   |   |   |
|---|---|---|---|---|
|**Fase**|**Duração**|**Objetivo Principal**|**Meses**|**Marco de Entrega (Gate)**|
|**Fase 0 — Fundação**|4 semanas|Infraestrutura, CI/CD, Identidade, base de dados|Mês 1|Cluster K8s operacional; svc-identity e svc-escolas com testes|
|**Fase 1 — Núcleo**|8 semanas|Pessoas, Matrículas, Académico, Notas/Faltas|Mês 2–3|MVP: escola piloto em produção, portais básicos funcionais|
|**Fase 2 — Operacional**|8 semanas|Financeiro, Concursos/Provas (ANEP), Vocacional|Mês 4–5|Escola(s) piloto com financeiro e provas online operacionais|
|**Fase 3 — Completo**|4 semanas|Relatórios MED/INE, Offline, Integrações, QA final|Mês 6|Versão 1.0 homologada e em produção; formações concluídas|

**3. Diagrama de Gantt — 6 Meses (24 Semanas)**

**Cada linha representa uma atividade. As barras coloridas indicam as semanas de execução.**

  

**4. Detalhe das Tarefas por Fase**

|   |   |   |   |   |   |
|---|---|---|---|---|---|
|**Fase 0 — Fundação**  (Semanas 1–4)|   |   |   |   |   |
|**Tarefa**|**Semanas**|**Responsável**|**Dependência**|**Prioridade**|**Entregável**|
|Criar repositórios + estrutura monorepo|S1|DevOps|—|Alta|Repositórios no GitHub, README, branching strategy|
|Configurar Docker Compose (dev) + servidor staging|S1–2|DevOps|—|Alta|Ambiente de desenvolvimento local e staging operacional|
|Pipeline CI/CD base (GitHub Actions)|S1–2|DevOps|Repo|Alta|Build, test, deploy automatizados|
|Instalar e configurar Keycloak|S2|Backend 1|Staging|Alta|SSO funcional, realms configurados|
|Módulo identity: utilizadores, papéis, JWT|S2–3|Backend 1|Keycloak|Alta|API de autenticação testada|
|Módulo escolas: CRUD escolas e anos letivos|S3–4|Backend 2|identity|Alta|API de escolas com testes unitários e integração|
|Nginx reverse proxy configurado|S3–4|DevOps|identity|Alta|Roteamento, rate-limit, JWT validation|
|Observabilidade base (Prometheus + Grafana)|S4|DevOps|Staging|Média|Dashboards básicos operacionais|
|Setup PostgreSQL único (schemas por módulo) + Redis|S1–2|DevOps|Staging|Alta|BD provisionada com schemas, backups automáticos|
|Documentação de API (Swagger/OpenAPI)|S3–4|Backend 1+2|Módulos|Média|Swagger UI acessível|

  

|   |   |   |   |   |   |
|---|---|---|---|---|---|
|**Fase 1 — Núcleo (MVP)**  (Semanas 4–12)|   |   |   |   |   |
|**Tarefa**|**Semanas**|**Responsável**|**Dependência**|**Prioridade**|**Entregável**|
|Módulo directory: pessoas, alunos, professores|S4–6|Backend 2|Fase 0|Alta|CRUD pessoas com validação de BI único|
|Módulo directory: vínculos aluno-encarregado|S6–7|Backend 2|directory|Alta|Associação com encarregado principal|
|Módulo enrollment: matrículas presencial|S5–8|Backend 1|directory|Alta|Fluxo completo: pedido → aprovação → alocação|
|Módulo enrollment: transferências|S7–8|Backend 1|enrollment|Alta|Transferências com histórico e documentos|
|Módulo academico: currículo e turmas|S6–8|Backend 2|enrollment|Alta|CRUD turmas, disciplinas, alocação de professores|
|Módulo academico: horários e diário de classe|S8–9|Backend 2|academico|Alta|Horários com deteção de conflitos|
|Módulo avaliacoes: notas e avaliações|S7–9|Backend 1|academico|Alta|Lançamento de notas, regras de média|
|Módulo avaliacoes: faltas e boletins|S9–10|Backend 1|avaliacoes|Alta|Faltas com limites, geração de boletim PDF|
|Frontend: Portal Aluno e Encarregado|S5–10|Frontend|API|Alta|Boletim, faltas, horário, comunicados|
|Frontend: Portal Professor|S6–10|Frontend|API|Alta|Lançamento de notas/faltas, diário|
|Frontend: Portal Direção/Secretaria|S7–11|Frontend|API|Alta|Matrículas, turmas, relatórios básicos|
|Frontend: Portal Gestão Provincial/Nacional|S10–12|Frontend|API|Média|Dashboards consolidados com indicadores|
|Testes E2E do fluxo académico completo|S10–12|QA|Frontend|Alta|Suite de testes automatizados com Playwright|
|Deploy MVP em escola piloto (staging)|S11–12|DevOps|All|Alta|MVP validado em ambiente real com dados reais|
|Importação dados históricos (CSV/Excel)|S10–12|Backend 1+2|API|Média|Ferramenta de importação com validação|

  

|   |   |   |   |   |   |
|---|---|---|---|---|---|
|**Fase 2 — Operacional**  (Semanas 13–20)|   |   |   |   |   |
|**Tarefa**|**Semanas**|**Responsável**|**Dependência**|**Prioridade**|**Entregável**|
|Módulo financeiro: planos e faturas|S13–14|Backend 1|enrollment|Alta|Geração automática de faturas mensais|
|Módulo financeiro: pagamentos e caixa|S14–15|Backend 1|financeiro|Alta|Registo de pagamentos, conciliação|
|Módulo financeiro: bolsas e descontos|S15–16|Backend 2|financeiro|Alta|Aplicação automática na faturação|
|Integração Multicaixa Express|S16|Backend 1|financeiro|Alta|Gateway de pagamento em produção|
|Módulo provas: concursos e banco de questões|S13–15|Backend 2|academico|Alta|CRUD concursos, questões, inscrições|
|Módulo provas: aplicação de prova digital|S15–16|Backend 2|provas|Alta|Prova online com timer e antifraude básico|
|Módulo provas: rankings e resultados|S16|Backend 2|provas|Alta|Rankings escola/município/nacional|
|Módulo vocacional: questionários|S15–17|Backend 1|directory|Média|Questionários vocacionais para classes 9–12|
|Módulo vocacional: perfis e relatórios|S17–18|Backend 1|vocacional|Média|Relatório PDF personalizado por aluno|
|Módulo notificacoes: e-mail e push|S14–16|Backend 2|todos|Média|Notificações de faltas, vencimento, resultados|
|App Mobile React Native — Portal Aluno|S14–18|Mobile|API|Média|Boletim, faltas, concursos no smartphone|
|App Mobile — Portal Encarregado|S16–20|Mobile|API|Média|Notificações, propinas, resultados|
|Frontend: módulo financeiro|S14–18|Frontend|API|Alta|Extrato, faturas, pagamentos na web|
|Frontend: módulo concursos/provas|S15–18|Frontend|API|Alta|Inscrição, aplicação, ranking|
|Testes E2E financeiro e provas|S18–20|QA|Frontend|Alta|Cobertura ≥ 80% nos novos módulos|

  

|   |   |   |   |   |   |
|---|---|---|---|---|---|
|**Fase 3 — Versão 1.0 Completa**  (Semanas 20–24)|   |   |   |   |   |
|**Tarefa**|**Semanas**|**Responsável**|**Dependência**|**Prioridade**|**Entregável**|
|Módulo relatorios: templates SIGE e INE|S19–21|Backend 1|all|Alta|Relatórios oficiais exportáveis em xlsx/pdf|
|Módulo relatorios: geração assíncrona|S20–21|Backend 1|relatorios|Alta|Jobs assíncronos com notificação ao utilizador|
|Auditoria e conformidade com dados pessoais|S19–20|Backend 2|identity|Alta|Conformidade com legislação angolana|
|Admin local offline (Tauri + SQLite)|S19–22|Backend 2 + DevOps|sync|Alta|App desktop instalável para secretarias offline|
|Módulo sync: sincronização local/nuvem|S20–22|Backend 2|API|Alta|Delta sync, outbox, conflict resolution|
|Módulo integracoes: SIUGEP e INE/GEPE|S20–22|Backend 1|relatorios|Média|Adaptadores com fila e retry automático|
|Módulo estoque: uniformes e livros|S20–22|Backend 2|directory|Baixa|Inventário, atribuição, alertas|
|Módulo alimentacao: refeições e subsídios|S21–23|Backend 2|financial|Baixa|Cardápio, consumo, gestão de subsídios|
|Testes de carga e stress (K6/Locust)|S22–23|DevOps + QA|all|Alta|Validar 10.000 utilizadores simultâneos|
|Penetration Testing (OWASP Top 10)|S22–23|QA + Externo|all|Alta|Relatório de pentest e correções|
|Formação de administradores e secretarias|S22–24|Analista|Escola piloto|Alta|Manual de utilizador + workshops presenciais|
|Formação de professores|S23–24|Analista|Escola piloto|Alta|Tutorial em vídeo + guia rápido|
|Deploy Versão 1.0 em produção|S24|DevOps|All|Alta|Deploy com rollback preparado|
|Relatório final e handover técnico|S24|Analista|All|Alta|Documentação técnica completa, runbooks|

  

**5. Marcos do Projeto (Milestones)**

|   |   |   |   |
|---|---|---|---|
|**Marco**|**Semana**|**Data (estimada)**|**Critério de Aceitação**|
|**M0**|S4|Abril 2026 (semana 4)|Infraestrutura operacional, módulos identity e escolas com testes passando, CI/CD funcional|
|**M1 — MVP**|S12|Junho 2026 (semana 12)|Escola piloto em produção: matrículas, turmas, notas e faltas funcionais; portais Aluno, Professor e Diretor operacionais|
|**M2 — Financeiro**|S16|Julho 2026 (semana 16)|Financeiro em produção na escola piloto; pelo menos 1 pagamento via Multicaixa Express processado com sucesso|
|**M3 — Provas ANEP**|S16|Julho 2026 (semana 16)|Plataforma de provas online homologada com a ANEP; 1 concurso-piloto aplicado com resultados e ranking publicados|
|**M4 — Versão 1.0**|S24|Setembro 2026 (semana 24)|Sistema completo em produção: relatórios SIGE/INE exportados, modo offline validado, pentest concluído, formações realizadas, ≥ 80% cobertura de testes|
|**M5 — Expansão**|S36+|2026–2027 (pós v1.0)|Expansão para todas as escolas de 2+ províncias; BI ministerial; app mobile completa; gerador automático de horários|

  

**6. Alocação da Equipa por Fase**

|   |   |   |   |   |   |
|---|---|---|---|---|---|
|**Perfil**|**Fase 0 (S1–4)**|**Fase 1 (S5–12)**|**Fase 2 (S13–20)**|**Fase 3 (S21–24)**|**Responsabilidades Principais**|
|Backend Engineer 1 (Python)|100%|100%|100%|100%|identity, enrollment, avaliacoes, financeiro, relatorios|
|Backend Engineer 2 (Python)|100%|100%|100%|100%|escolas, directory, academico, provas, vocacional, sync, estoque|
|Frontend Engineer (React)|50%|100%|100%|100%|Todos os portais web (Aluno, Prof, Direção, Gestão)|
|Mobile Engineer (React Native)|0%|25%|100%|75%|Apps Aluno e Encarregado (iOS/Android)|
|DevOps / Infraestrutura|100%|50%|50%|100%|K8s, CI/CD, observabilidade, segurança, testes de carga|
|Analista de Negócios / QA|75%|100%|100%|100%|Requisitos, testes E2E, documentação, formações|

  

**7. Riscos e Plano de Mitigação**

|   |   |   |   |
|---|---|---|---|
|**Risco**|**Probabilidade**|**Impacto**|**Mitigação**|
|Aderência lenta de escolas|Alta|Alto|Piloto com 3 escolas-chave desde o MVP; formação intensiva; suporte dedicado; envolver ANEP e Direções Provinciais como promotores|
|Conectividade instável nas escolas|Alta|Alto|Admin local offline prioritário (Fase 3); testes de sincronização com latência simulada; modo degradado gracioso|
|Atrasos em integrações gov. (SIUGEP, INE)|Média|Médio|Adaptadores com mock para desenvolvimento; integrações governamentais fora do caminho crítico (MVP sem elas); acordos institucionais antecipados|
|Resistência cultural ao sistema digital|Alta|Alto|UX simples e intuitivo como requisito de design; formações presenciais nas escolas piloto; documentação em português angolano|
|Dados históricos heterogéneos (migração SIGE)|Alta|Médio|Fase dedicada de importação (S10–12); ferramenta de pré-validação e normalização; sem bloqueio do MVP — dados históricos são opcionais|
|Saída de membro crítico da equipa|Baixa|Alto|Documentação técnica contínua (ADRs, runbooks); par programming e revisão de código cruzada; processo de onboarding de novos membros documentado|
|Vulnerabilidade de segurança em produção|Baixa|Crítico|SAST/DAST no CI/CD; pentest antes da v1.0; conformidade OWASP Top 10; plano de resposta a incidentes preparado antes do deploy|

  

**8. Critérios de Qualidade e Definição de Pronto (DoD)**

**8.1 Definição de Pronto por Sprint**

- Testes unitários passando com cobertura ≥ 80% do código novo;
- Testes de integração passando em ambiente de staging;
- Documentação OpenAPI atualizada para novos/alterados endpoints;
- Code review aprovado por pelo menos 1 outro membro da equipa;
- Deploy em staging executado com sucesso pelo CI/CD;
- Nenhuma vulnerabilidade crítica nova detetada pelo SAST.

  

**8.2 Critérios de Aceitação do MVP (Semana 12)**

- Escola piloto com ≥ 100 alunos matriculados no sistema;
- Professores a lançar notas via portal (sem papel);
- Portais de Aluno, Encarregado, Professor e Diretor operacionais;
- Tempo de resposta p95 ≤ 3s em condições normais;
- Zero incidentes críticos de segurança nos últimos 7 dias;
- Formação de utilizadores da escola piloto concluída.

  

**8.3 Critérios de Aceitação da Versão 1.0 (Semana 24)**

- Todos os módulos do âmbito (RF-01 a RF-13) implementados e testados;
- Relatórios SIGE e INE exportados e validados pelo MED/GEPE;
- Modo offline validado com teste de 72h sem conectividade e sincronização bem-sucedida;
- Pentest externo concluído sem vulnerabilidades críticas abertas;
- Cobertura de testes ≥ 80% (unitários + integração);
- Testes de carga com 10.000 utilizadores simultâneos sem degradação;
- Documentação técnica completa (README, ADRs, API docs, runbooks, manual do utilizador);
- Formações concluídas em todas as escolas piloto.