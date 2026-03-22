|                                                                                                                       |
| --------------------------------------------------------------------------------------------------------------------- |
| **SIENA**<br><br>Sistema de Integração Educacional Nacional de Angola<br><br>━━━━━━━━━━━━━━━━━━━━                     |
| **SN 8 — Roadmap Fase 1.1: Polimento, Dados e Formulários**                                                          |
| Versão 1.0  \|  Março 2026<br><br>_Fechar todos os módulos existentes numa versão viável — UX, dados reais e formulários completos_ |

---

## Objetivo

Antes de avançar para novos módulos, **fechar por completo** os módulos já implementados (Directory, Enrollment, Académico, Avaliações) e os 5 portais existentes. No final desta fase:

1. **Zero UUIDs visíveis** — todos os campos mostram nomes legíveis (aluno, professor, encarregado, disciplina)
2. **Formulários completos** — dropdowns/autocomplete em vez de campos de texto UUID
3. **Portais com dados reais** — dashboards com indicadores, tabelas com informação útil
4. **Fluxos end-to-end testáveis** — um utilizador real consegue completar todas as operações sem ajuda técnica

---

## Legenda

| Símbolo | Significado |
|---------|-------------|
| ⬜ | Não iniciado |
| 🔄 | Em progresso |
| ✅ | Concluído |

---

## Divisão de Trabalho

| Dev | Foco Principal | Portais |
|-----|---------------|---------|
| **Dev A** | Backend (APIs, DTOs, lookups, seeds) + Portal Admin | Correcções API + Admin + Gestão (backend) |
| **Dev B** | Frontend (formulários, tabelas, UX, portais) | Gestão (frontend) + Professor + Aluno + Encarregado |

> Os devs podem trabalhar em paralelo: Dev A prepara os endpoints e DTOs enriquecidos, Dev B consome-os nos portais.

---

## Sprint 1 — Resolução de UUIDs e DTOs Enriquecidos (Semana 1-2)

### Problema Central
Múltiplas páginas mostram UUIDs truncados (`a3f2b1c8...`) em vez de nomes. A causa raiz é que as APIs devolvem apenas IDs de entidades relacionadas sem resolver os nomes.

### Dev A — Backend: DTOs e Endpoints de Lookup

| # | Tarefa | Estado | Ficheiros Principais | Notas |
|---|--------|--------|---------------------|-------|
| 1 | Enriquecer DTO de Matrícula: incluir `aluno_nome`, `ano_letivo_descricao`, `classe_nome` | ⬜ | `enrollment/api/dtos.py`, `enrollment/application/service.py` | JOIN com `directory.pessoa` e `escolas.ano_letivo` |
| 2 | Enriquecer DTO de Turma: incluir `professor_regente_nome`, nomes das disciplinas | ⬜ | `academico/api/dtos.py`, `academico/application/service.py` | JOIN com `directory.pessoa` |
| 3 | Enriquecer DTO de Horário: incluir `disciplina_nome`, `professor_nome` | ⬜ | `academico/api/dtos.py` | Em vez de só `disciplina_id` e `professor_id` |
| 4 | Enriquecer DTO de Nota/Avaliação: incluir `aluno_nome`, `disciplina_nome` | ⬜ | `avaliacoes/api/dtos.py` | Para pauta e boletim |
| 5 | Enriquecer DTO de Falta: incluir `aluno_nome`, `disciplina_nome` | ⬜ | `avaliacoes/api/dtos.py` | Para listagem de faltas |
| 6 | Criar endpoint `GET /api/v1/alunos/lookup` — retorna `[{id, nome}]` simplificado | ⬜ | `directory/api/routes.py` | Para dropdowns nos formulários |
| 7 | Criar endpoint `GET /api/v1/professores/lookup` — retorna `[{id, nome}]` | ⬜ | `directory/api/routes.py` | Para dropdowns |
| 8 | Criar endpoint `GET /api/v1/disciplinas/lookup` — retorna `[{id, nome}]` | ⬜ | `academico/api/routes.py` | Para dropdowns |
| 9 | Criar endpoint `GET /api/v1/turmas/lookup` — retorna `[{id, nome, classe}]` | ⬜ | `academico/api/routes.py` | Para dropdowns |
| 10 | Criar endpoint `GET /api/v1/encarregados/lookup` — retorna `[{id, nome}]` | ⬜ | `directory/api/routes.py` | Para dropdowns |
| 11 | Criar endpoint `GET /api/v1/anos-letivos/lookup` — retorna `[{id, descricao}]` | ⬜ | `escolas/api/routes.py` | Para dropdowns |

### Dev B — Frontend: Substituir UUIDs por Nomes nas Tabelas

| # | Tarefa | Estado | Ficheiros Principais | Notas |
|---|--------|--------|---------------------|-------|
| 12 | Matriculas.tsx — substituir `aluno_id.slice(0,8)` pelo nome do aluno | ⬜ | `portals/gestao/Matriculas.tsx` | Usar campo `aluno_nome` do DTO enriquecido |
| 13 | Matriculas.tsx — mostrar `ano_letivo` como descrição em vez de UUID | ⬜ | `portals/gestao/Matriculas.tsx` | |
| 14 | Pauta.tsx — substituir `aluno_id.substring(0,8)` pelo nome do aluno | ⬜ | `portals/gestao/Pauta.tsx` | Crítico para pauta de notas |
| 15 | Turmas.tsx — mostrar nome do professor regente em vez de UUID | ⬜ | `portals/gestao/Turmas.tsx` | Já parcialmente feito, verificar |
| 16 | Turmas.tsx — detalhe: disciplinas e professores com nomes | ⬜ | `portals/gestao/Turmas.tsx` | No painel de detalhe |
| 17 | LancarNotas.tsx — substituir `aluno_id` completo pelo nome do aluno | ⬜ | `portals/professor/LancarNotas.tsx` | Tabela de lançamento |
| 18 | Horarios.tsx — mostrar professor e disciplina por nome no grid | ⬜ | `portals/gestao/Horarios.tsx` | |
| 19 | MinhasFaltas.tsx — mostrar disciplina por nome | ⬜ | `portals/aluno/MinhasFaltas.tsx` | |
| 20 | Boletim.tsx — resolver nomes de disciplinas | ⬜ | `portals/aluno/Boletim.tsx` | |

---

## Sprint 2 — Formulários com Dropdowns e Autocomplete (Semana 2-3)

### Dev A — Backend: Validações e Suporte a Formulários

| # | Tarefa | Estado | Ficheiros Principais | Notas |
|---|--------|--------|---------------------|-------|
| 21 | Endpoint `GET /api/v1/turmas/{id}/alunos` — lista alunos alocados com nome | ⬜ | `academico/api/routes.py` | Para o professor ver quem está na turma |
| 22 | Endpoint `GET /api/v1/professores/{id}/turmas` — turmas do professor | ⬜ | `academico/api/routes.py` | Para portal professor |
| 23 | Endpoint `GET /api/v1/professores/{id}/disciplinas` — disciplinas do professor | ⬜ | `academico/api/routes.py` | Para dropdown no lançamento de notas |
| 24 | Validação de encarregado obrigatório na matrícula | ⬜ | `enrollment/application/service.py` | Aluno deve ter pelo menos 1 vínculo |
| 25 | Endpoint `GET /api/v1/alunos/{id}/encarregados` — retornar nomes dos encarregados | ⬜ | `directory/api/routes.py` | Para detalhe do aluno |
| 26 | Melhorar paginação: adicionar `total_count` em todas as listagens | ⬜ | `common/schemas.py` | Para paginação no frontend |

### Dev B — Frontend: Formulários com Selects/Dropdowns

| # | Tarefa | Estado | Ficheiros Principais | Notas |
|---|--------|--------|---------------------|-------|
| 27 | Matriculas — dropdown de aluno (pesquisa por nome) em vez de campo UUID | ⬜ | `portals/gestao/Matriculas.tsx` | Usar endpoint `/alunos/lookup` |
| 28 | Matriculas — dropdown de ano letivo em vez de campo UUID | ⬜ | `portals/gestao/Matriculas.tsx` | Usar endpoint `/anos-letivos/lookup` |
| 29 | Turmas — dropdown de professor regente (já existe, validar) | ⬜ | `portals/gestao/Turmas.tsx` | |
| 30 | Turmas — dropdown de disciplinas ao criar turma | ⬜ | `portals/gestao/Turmas.tsx` | Multi-select com disciplinas do currículo |
| 31 | LancarNotas — dropdown de turma em vez de input | ⬜ | `portals/professor/LancarNotas.tsx` | Filtrar pelas turmas do professor logado |
| 32 | LancarNotas — dropdown de disciplina filtrada pela turma | ⬜ | `portals/professor/LancarNotas.tsx` | Cascata: turma → disciplinas |
| 33 | LancarNotas — lista de alunos automática ao selecionar turma | ⬜ | `portals/professor/LancarNotas.tsx` | Sem input manual de aluno_id |
| 34 | Horarios — dropdown de professor e disciplina ao criar horário | ⬜ | `portals/gestao/Horarios.tsx` | |
| 35 | Encarregados — formulário de criação com associação ao aluno | ⬜ | `portals/gestao/Encarregados.tsx` | Dropdown de aluno para vincular |
| 36 | Alunos — formulário: campo de encarregado com dropdown/busca | ⬜ | `portals/gestao/Alunos.tsx` | Vincular na criação do aluno |
| 37 | Criar componente reutilizável `<EntitySelect>` para lookups | ⬜ | `shared/components/EntitySelect.tsx` | Props: endpoint, label, value, onChange |

---

## Sprint 3 — Portais com Dados Reais e Dashboards (Semana 3-4)

### Dev A — Backend: Endpoints de Dashboard e Estatísticas

| # | Tarefa | Estado | Ficheiros Principais | Notas |
|---|--------|--------|---------------------|-------|
| 38 | Endpoint `GET /api/v1/dashboard/gestao` — stats da escola | ⬜ | `escolas/api/routes.py` | total_alunos, total_professores, total_turmas, matriculas_pendentes |
| 39 | Endpoint `GET /api/v1/dashboard/professor` — stats do professor | ⬜ | `academico/api/routes.py` | turmas_atribuidas, proximas_aulas, notas_por_lancar |
| 40 | Endpoint `GET /api/v1/dashboard/aluno` — stats do aluno | ⬜ | `avaliacoes/api/routes.py` | media_geral, total_faltas, proximas_avaliacoes |
| 41 | Endpoint `GET /api/v1/dashboard/encarregado` — stats dos educandos | ⬜ | `directory/api/routes.py` | lista_educandos com media e faltas |
| 42 | Endpoint `GET /api/v1/alunos/{id}/boletim?periodo=X` — boletim completo | ⬜ | `avaliacoes/api/routes.py` | Disciplinas + notas + médias calculadas |
| 43 | Endpoint `GET /api/v1/turmas/{id}/pauta` — pauta completa com nomes | ⬜ | `avaliacoes/api/routes.py` | Grid aluno × disciplina com médias |

### Dev B — Frontend: Dashboards e Páginas de Dados

| # | Tarefa | Estado | Ficheiros Principais | Notas |
|---|--------|--------|---------------------|-------|
| 44 | Dashboard Gestão — cards com dados reais (alunos, professores, turmas, matrículas) | ⬜ | `portals/gestao/Dashboard.tsx` | Consumir `/dashboard/gestao` |
| 45 | Dashboard Gestão — gráfico de matrículas por estado | ⬜ | `portals/gestao/Dashboard.tsx` | Pendentes vs aprovadas vs rejeitadas |
| 46 | Dashboard Professor — turmas atribuídas com indicadores | ⬜ | `portals/professor/Dashboard.tsx` | Consumir `/dashboard/professor` |
| 47 | Dashboard Aluno — resumo de notas e faltas | ⬜ | `portals/aluno/Dashboard.tsx` | Consumir `/dashboard/aluno` |
| 48 | Portal Encarregado — lista de educandos com resumo | ⬜ | `portals/encarregado/EncarregadoView.tsx` | Consumir `/dashboard/encarregado` |
| 49 | Portal Encarregado — ver boletim de cada educando | ⬜ | `portals/encarregado/EncarregadoView.tsx` | Seleccionar educando → ver boletim |
| 50 | Portal Encarregado — ver faltas de cada educando | ⬜ | `portals/encarregado/EncarregadoView.tsx` | |
| 51 | Boletim.tsx (aluno) — tabela formatada com notas por período e disciplina | ⬜ | `portals/aluno/Boletim.tsx` | Consumir `/alunos/{id}/boletim` |
| 52 | MinhasFaltas.tsx — tabela com tipo, disciplina, data, justificação | ⬜ | `portals/aluno/MinhasFaltas.tsx` | |
| 53 | HorarioAluno.tsx — grid semanal visual | ⬜ | `portals/aluno/HorarioAluno.tsx` | Estilo similar ao grid de gestão |

---

## Sprint 4 — Portal Admin, Detalhes e Fluxos Completos (Semana 4-5)

### Dev A — Backend: Admin e Seed Completo

| # | Tarefa | Estado | Ficheiros Principais | Notas |
|---|--------|--------|---------------------|-------|
| 54 | Endpoint `GET /api/v1/admin/tenants` — lista todos os tenants (super_admin) | ⬜ | `identity/api/routes.py` | Para portal admin |
| 55 | Endpoint `GET /api/v1/admin/tenants/{id}/stats` — stats por tenant | ⬜ | `identity/api/routes.py` | alunos, professores, turmas |
| 56 | Endpoint `POST /api/v1/admin/escolas` — criar escola + tenant + director | ⬜ | `escolas/api/routes.py` | Fluxo completo de onboarding |
| 57 | Script de seed completo para escola piloto | ⬜ | `application/seed.py` | 50 alunos, 10 professores, 40 encarregados, vínculos, matrículas, turmas, horários, notas do 1º período |
| 58 | Seed de currículo angolano realista (7ª-12ª classe) | ⬜ | `application/seed.py` | Disciplinas: Português, Matemática, Física, Química, Biologia, História, Geografia, Ed. Física, etc. |
| 59 | Validação de integridade: aluno sem matrícula não pode ter notas | ⬜ | `avaliacoes/application/service.py` | |
| 60 | Soft delete em cascata: desactivar aluno desactiva matrículas | ⬜ | `directory/application/service.py` | |

### Dev B — Frontend: Admin e Fluxos UX

| # | Tarefa | Estado | Ficheiros Principais | Notas |
|---|--------|--------|---------------------|-------|
| 61 | Portal Admin — Dashboard com lista de tenants/escolas e stats | ⬜ | `portals/admin/DashboardAdmin.tsx` | Cards por escola com indicadores |
| 62 | Portal Admin — formulário de criação de escola melhorado | ⬜ | `portals/admin/EscolasAdmin.tsx` | Tabs: dados escola + director + configuração |
| 63 | Detalhe do Aluno — página com tabs (dados, matrículas, notas, faltas, encarregados) | ⬜ | `portals/gestao/Alunos.tsx` | Vista completa do aluno |
| 64 | Detalhe do Professor — página com tabs (dados, turmas, horário) | ⬜ | `portals/gestao/Professores.tsx` | Vista completa do professor |
| 65 | Detalhe do Encarregado — página com educandos associados | ⬜ | `portals/gestao/Encarregados.tsx` | Lista de vínculos |
| 66 | MinhasTurmas.tsx (professor) — lista com contagem de alunos e disciplinas | ⬜ | `portals/professor/MinhasTurmas.tsx` | Dados reais |
| 67 | Diário de Classe — formulário de presença com checkboxes | ⬜ | `portals/professor/MinhasTurmas.tsx` | Checkbox por aluno + observações |
| 68 | Fluxo de matrícula completo: criar pedido → aprovar → alocar em turma | ⬜ | `portals/gestao/Matriculas.tsx` | Workflow visual com estados |

---

## Sprint 5 — Polimento, UX e Validação Final (Semana 5-6)

### Dev A — Backend: Performance e Qualidade

| # | Tarefa | Estado | Ficheiros Principais | Notas |
|---|--------|--------|---------------------|-------|
| 69 | Optimizar queries N+1: eager loading em listagens | ⬜ | Todos os repositories | `joinedload()` / `selectinload()` |
| 70 | Adicionar índices para queries frequentes | ⬜ | Migrations | `nome_completo`, `n_processo`, `bi_identificacao` |
| 71 | Validação de dados: campos obrigatórios em todos os endpoints | ⬜ | Todos os DTOs | Pydantic validators |
| 72 | Tratamento de erros consistente: mensagens em PT-PT | ⬜ | `common/exceptions.py` | Mensagens claras para o utilizador |
| 73 | Logs estruturados em todas as operações críticas | ⬜ | Todos os services | `structlog` ou `logging` com contexto |
| 74 | Testes de integração para os fluxos principais | ⬜ | `tests/` | Matrícula, notas, boletim |

### Dev B — Frontend: UX e Consistência Visual

| # | Tarefa | Estado | Ficheiros Principais | Notas |
|---|--------|--------|---------------------|-------|
| 75 | Feedback visual: loading states em todas as tabelas e formulários | ⬜ | Todos os portais | Spinners, skeleton screens |
| 76 | Mensagens de sucesso/erro com toast notifications | ⬜ | `shared/components/Toast.tsx` | Em vez de `alert()` |
| 77 | Confirmação antes de acções destrutivas (eliminar, rejeitar) | ⬜ | Todos os portais | Modal de confirmação |
| 78 | Responsividade: testar e corrigir em tablet (1024px) | ⬜ | CSS/estilos globais | Sidebar collapsible |
| 79 | Empty states: mensagens quando não há dados ("Nenhum aluno registado") | ⬜ | Todas as tabelas | Em vez de tabela vazia |
| 80 | Paginação no frontend: componente de paginação em tabelas grandes | ⬜ | `shared/components/Pagination.tsx` | Usar `total_count` da API |
| 81 | Breadcrumbs e navegação melhorada nos portais | ⬜ | Todos os portais | Saber onde o utilizador está |
| 82 | Validação de formulários no frontend (campos obrigatórios, formatos) | ⬜ | Todos os formulários | Feedback inline |

---

## Sprint 6 — Integração, Seed e Validação MVP (Semana 6-7)

### Dev A + Dev B — Trabalho Conjunto

| # | Tarefa | Estado | Responsável | Notas |
|---|--------|--------|-------------|-------|
| 83 | Executar seed completo e validar dados nos portais | ⬜ | A + B | 50 alunos, 10 professores, turmas, notas |
| 84 | Teste E2E: login director → criar aluno → matricular → alocar em turma → ver pauta | ⬜ | B | Fluxo completo sem erros |
| 85 | Teste E2E: login professor → ver turmas → lançar notas → ver diário | ⬜ | B | |
| 86 | Teste E2E: login aluno → ver boletim → ver faltas → ver horário | ⬜ | B | |
| 87 | Teste E2E: login encarregado → ver educandos → ver boletim | ⬜ | B | |
| 88 | Teste E2E: login admin → criar escola → ver stats | ⬜ | A | |
| 89 | Corrigir todos os bugs encontrados nos testes | ⬜ | A + B | Sprint buffer |
| 90 | Documentar credenciais e fluxos de teste actualizados | ⬜ | A | Actualizar SN 7 |

---

## Resumo da Divisão por Dev

### Dev A — 40 tarefas (Backend + Admin)

| Sprint | Tarefas | Foco |
|--------|---------|------|
| Sprint 1 | #1–11 | DTOs enriquecidos + endpoints de lookup |
| Sprint 2 | #21–26 | Endpoints de suporte a formulários |
| Sprint 3 | #38–43 | Endpoints de dashboard e estatísticas |
| Sprint 4 | #54–60 | Admin API + seed completo |
| Sprint 5 | #69–74 | Performance + qualidade + testes |
| Sprint 6 | #83, #88–90 | Validação e bugs |

### Dev B — 50 tarefas (Frontend + UX)

| Sprint | Tarefas | Foco |
|--------|---------|------|
| Sprint 1 | #12–20 | Substituir UUIDs por nomes nas tabelas |
| Sprint 2 | #27–37 | Formulários com dropdowns |
| Sprint 3 | #44–53 | Dashboards e portais com dados |
| Sprint 4 | #61–68 | Admin frontend + detalhes + fluxos |
| Sprint 5 | #75–82 | UX, responsividade, validação |
| Sprint 6 | #84–87, #89 | Testes E2E e bugs |

---

## Dependências entre Sprints

```
Sprint 1 (Dev A: DTOs)  ──────► Sprint 1 (Dev B: Tabelas)
                                    │
Sprint 2 (Dev A: Endpoints) ──►Sprint 2 (Dev B: Formulários)
                                    │
Sprint 3 (Dev A: Dashboard) ──►Sprint 3 (Dev B: Dashboards UI)
                                    │
Sprint 4 (Dev A: Admin API) ──►Sprint 4 (Dev B: Admin UI)
                                    │
Sprint 5 (Dev A: Perf) ◄──────►Sprint 5 (Dev B: UX)
                                    │
                              Sprint 6 (Conjunto: Validação)
```

> **Nota:** Em cada sprint, Dev A deve terminar os endpoints antes de Dev B começar a consumi-los. Recomenda-se que Dev A comece 2-3 dias antes em cada sprint, ou que Dev B trabalhe com mocks enquanto espera.

---

## Critérios de Conclusão da Fase 1.1

| # | Critério | Validação |
|---|----------|-----------|
| 1 | Zero UUIDs visíveis em qualquer portal | Revisão visual de todas as páginas |
| 2 | Todos os formulários usam dropdowns/selects | Testar criação de matrícula, turma, nota |
| 3 | Dashboards com dados reais em todos os portais | Login com cada papel e verificar |
| 4 | Portal Encarregado funcional com dados dos educandos | Login encarregado → ver boletim |
| 5 | Seed de 50+ alunos com dados completos | Executar seed e verificar |
| 6 | 5 fluxos E2E sem erros | Director, professor, aluno, encarregado, admin |
| 7 | Loading states e mensagens de erro em PT | Verificar UX em estados edge |
| 8 | Paginação funcional em tabelas com >20 registos | Verificar com seed completo |

---

## Contadores

| Métrica | Valor |
|---------|-------|
| Sprints | 6 (estimativa: 6-7 semanas) |
| Tarefas total | 90 |
| Tarefas Dev A | 40 |
| Tarefas Dev B | 50 |
| Endpoints novos/modificados | ~20 |
| Páginas frontend modificadas | ~20 |
| Componentes reutilizáveis novos | 3-4 (EntitySelect, Pagination, Toast, EmptyState) |

---

## Depois desta fase

Com a Fase 1.1 concluída, o SIENA terá uma **versão viável** dos módulos core:
- Todos os portais funcionais com dados reais e UX polida
- Formulários intuitivos sem necessidade de conhecer UUIDs
- Seed completo para demonstração a stakeholders
- Base sólida para avançar para a **Fase 2 — Operacional** (financeiro, provas ANEP, vocacional, notificações, mobile)