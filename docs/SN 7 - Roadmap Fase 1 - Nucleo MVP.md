|                                                                                                                       |
| --------------------------------------------------------------------------------------------------------------------- |
| **SIENA**<br><br>Sistema de Integração Educacional Nacional de Angola<br><br>━━━━━━━━━━━━━━━━━━━━                     |
| **SN 7 — Roadmap Fase 1: Núcleo MVP**                                                                                 |
| Versão 1.0  \|  Março 2026<br><br>_Dos módulos base ao MVP funcional — directory, enrollment, académico, avaliações_   |

---

## Objetivo

Implementar os 4 módulos core que transformam o SIENA num sistema educacional funcional. No final desta fase, uma escola piloto deve conseguir:

1. Registar pessoas (alunos, professores, encarregados)
2. Matricular alunos e alocar em turmas
3. Definir currículos, horários e preencher diário de classe
4. Lançar notas, registar faltas e gerar boletins

A Fase 1 assume que a **Fase 0 está concluída** (identity + escolas + frontend login/dashboard).

---

## Legenda de Estado

| Símbolo | Significado |
|---------|-------------|
| ⬜ | Não iniciado |
| 🔄 | Em progresso |
| ✅ | Concluído |

---

## Pré-requisitos (da Fase 0)

| Requisito | Estado |
|-----------|--------|
| Identity module (auth, JWT, RBAC) | ✅ |
| Escolas module (CRUD, tenant isolation) | ✅ |
| Frontend login + dashboard | ✅ |
| Docker Compose local funcional | ✅ |
| Modelo relacional documentado (SN 6) | ✅ |

---

## Fase 1.0 — Módulo Directory (Gestão de Pessoas)

**Objetivo:** Registo centralizado de todas as pessoas no sistema com validação de BI único.

### 1.0.1 — Modelo de dados

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 1 | SQLAlchemy models: `pessoa`, `aluno`, `professor`, `encarregado`, `funcionario` | ⬜ | Schema `directory`, herdam `TenantBaseModel` |
| 2 | SQLAlchemy model: `vinculo_aluno_encarregado` | ⬜ | Tabela de associação com tipo e flag `principal` |
| 3 | Migration Alembic para todas as tabelas do schema `directory` | ⬜ | `alembic revision --autogenerate` |
| 4 | Seed: 5 alunos + 3 professores + 5 encarregados + vínculos | ⬜ | Dados de teste para escola piloto |

### 1.0.2 — Repository + Services

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 5 | `DirectoryRepository`: CRUD pessoa, aluno, professor, encarregado, funcionario | ⬜ | Todas as queries filtram por `tenant_id` |
| 6 | Validação de BI único por tenant | ⬜ | `UNIQUE (tenant_id, bi_identificacao)` — erro 409 se duplicado |
| 7 | `PessoaService`: criar/editar pessoa com tipo (aluno, professor, etc.) | ⬜ | Cria registo em `pessoa` + tabela específica |
| 8 | `VinculoService`: associar aluno-encarregado com validação de principal | ⬜ | Pelo menos 1 encarregado principal obrigatório |

### 1.0.3 — API endpoints

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 9 | `POST /api/v1/alunos` — regista aluno (pessoa + aluno) | ⬜ | Requer `secretaria` ou `diretor` |
| 10 | `GET /api/v1/alunos` — lista alunos (paginado, filtros) | ⬜ | Filtro: nome, n_processo, status |
| 11 | `GET /api/v1/alunos/{id}` — detalhe com encarregados | ⬜ | Include vínculos |
| 12 | `PATCH /api/v1/alunos/{id}` — edita dados do aluno | ⬜ | |
| 13 | `POST /api/v1/professores` — regista professor | ⬜ | Requer `diretor` |
| 14 | `GET /api/v1/professores` — lista professores | ⬜ | Filtro: especialidade, tipo_contrato |
| 15 | `GET /api/v1/professores/{id}` — detalhe do professor | ⬜ | |
| 16 | `PATCH /api/v1/professores/{id}` — edita professor | ⬜ | |
| 17 | `POST /api/v1/encarregados` — regista encarregado | ⬜ | |
| 18 | `GET /api/v1/encarregados` — lista encarregados | ⬜ | |
| 19 | `POST /api/v1/alunos/{id}/vinculos` — associa encarregado | ⬜ | Valida principal |
| 20 | `GET /api/v1/alunos/{id}/vinculos` — lista vínculos | ⬜ | |
| 21 | DTOs Pydantic para todos os endpoints | ⬜ | Request + Response models |

### 1.0.4 — Testes

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 22 | Testes unitários: PessoaService, VinculoService | ⬜ | |
| 23 | Teste de integração: BI duplicado retorna 409 | ⬜ | |
| 24 | Teste E2E: criar aluno → associar encarregado → listar | ⬜ | Via curl ou pytest |

---

## Fase 1.1 — Módulo Enrollment (Matrículas)

**Objetivo:** Fluxo completo de matrícula — pedido → aprovação → alocação em turma.

**Dependência:** Directory (1.0) + Escolas (Fase 0)

### 1.1.1 — Modelo de dados

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 25 | SQLAlchemy models: `matricula`, `alocacao_turma`, `transferencia`, `documento_matricula` | ⬜ | Schema `enrollment` |
| 26 | Migration Alembic para schema `enrollment` | ⬜ | FKs cross-schema: `directory.aluno`, `escolas.ano_letivo` |
| 27 | Seed: 5 matrículas aprovadas para a escola piloto | ⬜ | Ligadas aos alunos do seed de directory |

### 1.1.2 — Repository + Services

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 28 | `EnrollmentRepository`: CRUD matrícula, alocação, transferência | ⬜ | Cross-schema queries |
| 29 | `MatriculaService`: criar pedido → aprovar → rejeitar | ⬜ | Validação: aluno não pode ter 2 matrículas no mesmo ano |
| 30 | `AlocacaoService`: alocar aluno em turma | ⬜ | Validação: não exceder `capacidade_max` |
| 31 | `TransferenciaService`: pedido → aprovação → mover aluno | ⬜ | Cria matrícula na escola destino |

### 1.1.3 — API endpoints

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 32 | `POST /api/v1/matriculas` — novo pedido de matrícula | ⬜ | Requer `secretaria` ou `diretor` |
| 33 | `GET /api/v1/matriculas` — lista matrículas (filtros) | ⬜ | Filtro: ano_letivo, classe, estado, turno |
| 34 | `PATCH /api/v1/matriculas/{id}/aprovar` — aprova matrícula | ⬜ | Requer `diretor` |
| 35 | `PATCH /api/v1/matriculas/{id}/rejeitar` — rejeita matrícula | ⬜ | Com motivo |
| 36 | `POST /api/v1/matriculas/{id}/alocacao` — aloca em turma | ⬜ | Valida capacidade |
| 37 | `POST /api/v1/transferencias` — pedido de transferência | ⬜ | |
| 38 | `PATCH /api/v1/transferencias/{id}/aprovar` — aprova transferência | ⬜ | |
| 39 | `GET /api/v1/matriculas/{id}/documentos` — lista documentos | ⬜ | |
| 40 | `POST /api/v1/matriculas/{id}/documentos` — upload documento | ⬜ | Multipart upload |
| 41 | DTOs Pydantic para todos os endpoints | ⬜ | |

### 1.1.4 — Testes

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 42 | Teste: matrícula duplicada no mesmo ano → 409 | ⬜ | |
| 43 | Teste: alocação em turma cheia → 400 | ⬜ | |
| 44 | Teste E2E: matrícula → aprovação → alocação em turma | ⬜ | |

---

## Fase 1.2 — Módulo Académico (Turmas, Horários, Diário)

**Objetivo:** Definir currículos, criar turmas, gerar horários e preencher diário de classe.

**Dependência:** Enrollment (1.1) + Directory (1.0) + Escolas (Fase 0)

### 1.2.1 — Modelo de dados

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 45 | SQLAlchemy models: `curriculo`, `disciplina`, `turma` | ⬜ | Schema `academico` |
| 46 | SQLAlchemy models: `horario_aula`, `diario_classe`, `presenca_diario` | ⬜ | |
| 47 | Migration Alembic para schema `academico` | ⬜ | FKs: `escolas.ano_letivo`, `directory.professor`, `directory.aluno` |
| 48 | Seed: currículo 7.ª classe + 8 disciplinas + 2 turmas + horários | ⬜ | Dados realistas para Angola |

### 1.2.2 — Repository + Services

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 49 | `AcademicoRepository`: CRUD currículo, disciplina, turma, horário, diário | ⬜ | |
| 50 | `CurriculoService`: criar/editar currículo com disciplinas | ⬜ | |
| 51 | `TurmaService`: criar turma, atribuir professor regente | ⬜ | |
| 52 | `HorarioService`: criar horários com detecção de conflitos | ⬜ | Professor e sala não podem ter 2 aulas simultâneas |
| 53 | `DiarioService`: registar aula + presenças em lote | ⬜ | Apenas professor da disciplina pode preencher |

### 1.2.3 — API endpoints

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 54 | `POST /api/v1/curriculos` — cria currículo | ⬜ | Requer `diretor` |
| 55 | `GET /api/v1/curriculos` — lista currículos | ⬜ | |
| 56 | `POST /api/v1/disciplinas` — cria disciplina | ⬜ | Ligada a currículo |
| 57 | `GET /api/v1/disciplinas` — lista disciplinas | ⬜ | Filtro: currículo, classe |
| 58 | `POST /api/v1/turmas` — cria turma | ⬜ | Requer `diretor` |
| 59 | `GET /api/v1/turmas` — lista turmas | ⬜ | Filtro: ano_letivo, classe, turno |
| 60 | `GET /api/v1/turmas/{id}` — detalhe com alunos alocados | ⬜ | Include alunos via enrollment |
| 61 | `GET /api/v1/turmas/{id}/alunos` — lista alunos da turma | ⬜ | Via alocacao_turma |
| 62 | `POST /api/v1/turmas/{id}/horarios` — define horários | ⬜ | Com validação de conflitos |
| 63 | `GET /api/v1/turmas/{id}/horarios` — horário semanal | ⬜ | Grid dia×hora |
| 64 | `GET /api/v1/professores/{id}/horarios` — horário do professor | ⬜ | Agregação cross-turma |
| 65 | `POST /api/v1/diario` — regista aula + presenças | ⬜ | Requer `professor` |
| 66 | `GET /api/v1/turmas/{id}/diario` — histórico do diário | ⬜ | Filtro: disciplina, data |
| 67 | DTOs Pydantic para todos os endpoints | ⬜ | |

### 1.2.4 — Testes

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 68 | Teste: conflito de horário do professor → 409 | ⬜ | |
| 69 | Teste: conflito de sala → 409 | ⬜ | |
| 70 | Teste E2E: criar turma → definir horário → registar aula → presenças | ⬜ | |

---

## Fase 1.3 — Módulo Avaliações (Notas, Faltas, Boletins)

**Objetivo:** Lançamento de notas, registo de faltas com limites, e geração de boletins.

**Dependência:** Académico (1.2) + Directory (1.0)

### 1.3.1 — Modelo de dados

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 71 | SQLAlchemy models: `avaliacao`, `nota`, `falta` | ⬜ | Schema `avaliacoes` |
| 72 | SQLAlchemy models: `regra_media`, `boletim` | ⬜ | |
| 73 | Migration Alembic para schema `avaliacoes` | ⬜ | FKs: `academico.turma`, `academico.disciplina`, `directory.aluno` |
| 74 | Seed: regras de média para ensino primário e secundário | ⬜ | Configurável por escola |

### 1.3.2 — Repository + Services

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 75 | `AvaliacoesRepository`: CRUD avaliação, nota, falta, boletim | ⬜ | |
| 76 | `NotaService`: lançar notas com validação de limites | ⬜ | Valor ∈ [0, nota_maxima] |
| 77 | `FaltaService`: registar faltas com controlo de limite | ⬜ | Alerta quando ≥ 80% do máximo |
| 78 | `MediaService`: calcular média por disciplina e período | ⬜ | Usa regras de `regra_media` |
| 79 | `BoletimService`: gerar boletim (dados + PDF futuro) | ⬜ | JSON primeiro, PDF na Fase 2 |

### 1.3.3 — API endpoints

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 80 | `POST /api/v1/avaliacoes` — cria avaliação (teste, trabalho, exame) | ⬜ | Requer `professor` |
| 81 | `GET /api/v1/avaliacoes` — lista avaliações | ⬜ | Filtro: turma, disciplina, período |
| 82 | `POST /api/v1/avaliacoes/{id}/notas` — lança notas em lote | ⬜ | Array de {aluno_id, valor} |
| 83 | `GET /api/v1/avaliacoes/{id}/notas` — lista notas da avaliação | ⬜ | |
| 84 | `PATCH /api/v1/notas/{id}` — edita nota (janela editável) | ⬜ | |
| 85 | `POST /api/v1/faltas` — regista faltas em lote | ⬜ | Array de {aluno_id, disciplina_id, tipo} |
| 86 | `GET /api/v1/alunos/{id}/faltas` — faltas do aluno | ⬜ | Filtro: disciplina, tipo, período |
| 87 | `GET /api/v1/alunos/{id}/faltas/resumo` — resumo (total, por disciplina) | ⬜ | Com indicador de proximidade do limite |
| 88 | `GET /api/v1/alunos/{id}/notas` — notas do aluno por período | ⬜ | Agrupa por disciplina |
| 89 | `GET /api/v1/turmas/{id}/notas` — pauta da turma | ⬜ | Grid aluno × disciplina |
| 90 | `GET /api/v1/alunos/{id}/boletim?periodo=1` — boletim do aluno | ⬜ | JSON com médias calculadas |
| 91 | DTOs Pydantic para todos os endpoints | ⬜ | |

### 1.3.4 — Testes

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 92 | Teste: nota fora do intervalo → 400 | ⬜ | |
| 93 | Teste: faltas acima do limite → flag no resumo | ⬜ | |
| 94 | Teste: cálculo de média ponderada correcto | ⬜ | |
| 95 | Teste E2E: criar avaliação → lançar notas → ver boletim | ⬜ | |

---

## Fase 1.4 — Frontend: Portais por Perfil

**Objetivo:** Cada tipo de utilizador vê o portal adequado ao seu papel.

**Dependência:** Todos os módulos backend da Fase 1

### 1.4.1 — Portal Direção / Secretaria

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 96 | Página de gestão de alunos (lista, criar, editar, detalhe) | ⬜ | CRUD completo |
| 97 | Página de gestão de professores (lista, criar, editar) | ⬜ | |
| 98 | Página de gestão de encarregados (lista, criar, associar) | ⬜ | |
| 99 | Página de matrículas (lista pendentes, aprovar/rejeitar) | ⬜ | Workflow visual |
| 100 | Página de turmas (lista, criar, ver alunos) | ⬜ | |
| 101 | Página de currículos e disciplinas | ⬜ | |
| 102 | Página de horários (grid visual por turma) | ⬜ | Drag-and-drop futuro, grid simples agora |
| 103 | Página de pauta da turma (grid notas) | ⬜ | Tabela aluno × disciplina |
| 104 | Dashboard direção: indicadores (alunos, turmas, matrículas, faltas) | ⬜ | Gráficos com dados reais |

### 1.4.2 — Portal Professor

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 105 | Dashboard professor: turmas atribuídas, próximas aulas | ⬜ | |
| 106 | Página de minhas turmas (lista de turmas do professor) | ⬜ | |
| 107 | Página de diário de classe (registar aula + presenças) | ⬜ | Checkbox por aluno |
| 108 | Página de lançamento de notas (por avaliação) | ⬜ | Input por aluno com validação |
| 109 | Página de meu horário semanal | ⬜ | Grid visual |

### 1.4.3 — Portal Aluno / Encarregado

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 110 | Dashboard aluno: resumo de notas, faltas, horário | ⬜ | |
| 111 | Página de boletim (notas por período e disciplina) | ⬜ | |
| 112 | Página de faltas (lista com tipo e justificativa) | ⬜ | |
| 113 | Página de horário semanal | ⬜ | Grid visual |
| 114 | View de encarregado: ver boletim e faltas dos filhos | ⬜ | Seleciona educando |

### 1.4.4 — Navegação por papel

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 115 | Sidebar dinâmica baseada no papel do utilizador | ⬜ | Menus diferentes por papel |
| 116 | Routing protegido por papel (diretor vê X, professor vê Y) | ⬜ | `requireRole` no frontend |
| 117 | Página 403 (sem permissão) | ⬜ | |

### 1.4.5 — Testes Frontend

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 118 | Teste E2E: login diretor → criar aluno → matricular → alocar | ⬜ | |
| 119 | Teste E2E: login professor → registar aula → lançar notas | ⬜ | |
| 120 | Teste E2E: login aluno → ver boletim e faltas | ⬜ | |

---

## Fase 1.5 — Integração e Validação MVP

**Objetivo:** Tudo funciona end-to-end com dados realistas de uma escola angolana.

### 1.5.1 — Dados realistas

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 121 | Script de seed completo: escola com currículo angolano | ⬜ | 7.ª–12.ª classe, disciplinas reais |
| 122 | Seed: 100 alunos, 15 professores, 80 encarregados | ⬜ | Nomes angolanos realistas |
| 123 | Seed: 6 turmas com horários completos | ⬜ | 7.ª-A/B, 8.ª-A/B, 9.ª-A/B |
| 124 | Seed: matrículas aprovadas e alocações | ⬜ | ~16 alunos por turma |
| 125 | Seed: notas do 1.º período + faltas | ⬜ | Dados variados |

### 1.5.2 — Validação funcional

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 126 | Fluxo completo direção: registar aluno → matricular → ver pauta | ⬜ | |
| 127 | Fluxo completo professor: diário → notas → ver turma | ⬜ | |
| 128 | Fluxo completo aluno: ver boletim → faltas → horário | ⬜ | |
| 129 | Tenant isolation: criar 2.º tenant, confirmar isolamento | ⬜ | |
| 130 | Performance: todas as listas < 1s com 100 registos | ⬜ | |

### 1.5.3 — Importação de dados

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 131 | Endpoint de importação CSV/Excel de alunos | ⬜ | Upload + validação + preview |
| 132 | Endpoint de importação de notas históricas | ⬜ | Matching por n_processo |
| 133 | Tratamento de erros e relatório de importação | ⬜ | Linhas válidas vs. rejeitadas |

---

## Resumo dos Marcos — Fase 1

| Marco | Descrição | Tarefas | Estado | Critério de Sucesso |
|-------|-----------|---------|--------|---------------------|
| **M1.0** | Directory funcional | #1–24 | ⬜ | CRUD pessoas + vínculos via API e frontend |
| **M1.1** | Matrículas funcionais | #25–44 | ⬜ | Fluxo matrícula → aprovação → alocação em turma |
| **M1.2** | Académico funcional | #45–70 | ⬜ | Currículos, turmas, horários e diário operacionais |
| **M1.3** | Avaliações funcionais | #71–95 | ⬜ | Notas, faltas e boletins com cálculo de médias |
| **M1.4** | Portais frontend | #96–120 | ⬜ | 3 portais (direção, professor, aluno) funcionais no browser |
| **M1.5** | MVP validado | #121–133 | ⬜ | Escola piloto com 100 alunos, dados realistas, tudo funcional |

---

## Ordem de Implementação Recomendada

```
Fase 1.0 (Directory)        ████████░░░░░░░░░░░░░░░░░░░░
Fase 1.1 (Enrollment)       ░░░░████████░░░░░░░░░░░░░░░░
Fase 1.2 (Académico)        ░░░░░░░░████████░░░░░░░░░░░░
Fase 1.3 (Avaliações)       ░░░░░░░░░░░░████████░░░░░░░░
Fase 1.4 (Frontend)         ░░░░░░░░████████████████░░░░
Fase 1.5 (Validação MVP)    ░░░░░░░░░░░░░░░░░░░░████████
```

A Fase 1.4 (frontend) pode avançar em paralelo com o backend — à medida que cada módulo backend fica pronto, os portais correspondentes são construídos.

---

## Contadores

| Métrica | Valor |
|---------|-------|
| Sub-fases | 6 (1.0–1.5) |
| Tarefas total | 133 |
| Módulos backend | 4 (directory, enrollment, academico, avaliacoes) |
| Tabelas novas | 17 |
| Endpoints novos | ~45 |
| Portais frontend | 3 (direção, professor, aluno/encarregado) |
| Páginas frontend novas | ~25 |

---

## Depois desta fase

Com o M1.5 concluído, o SIENA terá o **MVP funcional** descrito no SN-4:
- Escola piloto com ≥ 100 alunos matriculados
- Professores a lançar notas via portal
- Portais Aluno, Professor e Diretor operacionais
- Boletins gerados automaticamente

A partir daqui, avançamos para a **Fase 2 — Operacional** (financeiro, provas ANEP, vocacional, notificações).