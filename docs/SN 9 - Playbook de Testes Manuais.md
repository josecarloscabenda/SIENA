---
título: SN 9 — Playbook de Testes Manuais (Fase 1.1)
sistema: SIENA
versão: 1.0
data: Abril 2026
tags: [siena, testes, qa, playbook, manual, fase-1.1]
---

# SIENA — Playbook de Testes Manuais
> Roteiro passo-a-passo para validar todas as funcionalidades da Fase 1.1 (Sprints 1–3).
>
> *Pega num PC, segue por ordem, marca `[x]` quando passar. Se algo falhar, regista o que viste.*

---

## Como usar este documento

- Cada funcionalidade tem **pré-condições**, **passos** e **resultado esperado**.
- A ordem importa — algumas secções dependem de dados criados nas anteriores.
- Se uma verificação falhar: anota no fundo do documento na secção *Bugs Encontrados* e prossegue (não bloqueies o teste todo num só erro).
- Para cada teste, valida as **3 dimensões**: API (resposta correcta), UI (visual + estado), regras de negócio (erros e validações).

---

## 0. Pré-Condições — Setup Limpo

### 0.1 Subir os serviços

```bash
cd /caminho/para/SIENA
docker compose up -d postgres redis backend
```

- [ ] `docker compose ps` mostra os 3 serviços `Up (healthy)` (postgres, redis, backend)
- [ ] `curl http://localhost:8000/api/health` devolve `{"status":"ok","service":"siena"}`

### 0.2 Aplicar migrations

```bash
docker compose exec backend alembic upgrade head
```

- [ ] Última linha mostra `e7f1a2b3c4d5 (head)` (ou versão posterior)

### 0.3 Correr seeds (ordem obrigatória)

```bash
# 1. Identity (tenant escola-piloto + papéis + admin)
docker compose exec backend python -m src.modules.identity.application.seed

# 2. Test users (diretor, secretaria, professor, aluno, encarregado)
docker compose exec backend python -m scripts.seed_test_users

# 3. MVP — 100 alunos, 15 profs, 80 encarregados, 6 turmas, notas, faltas
docker compose exec backend python -m scripts.seed_mvp
```

- [ ] Identity seed: cria 10 papéis + tenant `Escola Piloto SIENA` + user `admin`
- [ ] seed_test_users: cria os 5 utilizadores de teste sem erros
- [ ] seed_mvp: termina com `MVP Seed complete!` e mostra `Professores: 15 | Encarregados: 80 | Alunos: 100 | Turmas: 6`

### 0.4 Vincular utilizadores de teste a entidades reais

> Os 5 utilizadores do `seed_test_users` são criados sem `pessoa_id`. Para os portais funcionarem, precisamos de os ligar a um Professor / Aluno / Encarregado existente.

```bash
docker compose exec postgres psql -U siena -d siena -c "
-- Professor: liga ao primeiro professor do seed
UPDATE identity.utilizador
SET pessoa_id = (SELECT pessoa_id FROM directory.professor LIMIT 1)
WHERE username = 'professor';

-- Aluno: liga ao primeiro aluno
UPDATE identity.utilizador
SET pessoa_id = (SELECT pessoa_id FROM directory.aluno LIMIT 1)
WHERE username = 'aluno';

-- Encarregado: liga a um encarregado que tenha pelo menos 1 educando vinculado
UPDATE identity.utilizador
SET pessoa_id = (
  SELECT pessoa_id FROM directory.encarregado e
  WHERE EXISTS (SELECT 1 FROM directory.vinculo_aluno_encarregado v
                WHERE v.encarregado_id = e.id AND v.deleted_at IS NULL)
  LIMIT 1
)
WHERE username = 'encarregado';
"
```

- [ ] 3× `UPDATE 1` no output

### 0.5 Subir o frontend

```bash
cd frontend/web && npm install && npm run dev
```

- [ ] Vite arranca em `http://localhost:5173`
- [ ] Sem erros de TypeScript no terminal (`npx tsc --noEmit` se quiseres confirmar)

---

## 1. Credenciais de Teste

| Username | Password | Papel | Tenant |
|---|---|---|---|
| `admin` | `admin123` | super_admin | escola-piloto |
| `diretor` | `diretor123` | diretor | escola-piloto |
| `secretaria` | `secretaria123` | secretaria | escola-piloto |
| `professor` | `professor123` | professor | escola-piloto |
| `aluno` | `aluno123` | aluno | escola-piloto |
| `encarregado` | `encarregado123` | encarregado | escola-piloto |

---

## 2. Sprint 0 — Multi-tenant Login

### 2.1 Login URL genérico (selector de escola)

1. Abrir `http://localhost:5173/login`

- [ ] Página mostra **dropdown** "Escola" com pelo menos `Escola Piloto SIENA`
- [ ] Não há campo de UUID — só o dropdown
- [ ] Login com `admin / admin123` redirecciona para `/admin` (super_admin) ou `/gestao` consoante o papel

### 2.2 Login URL partilhável (`/escola/:slug/login`)

1. Logout. Abrir `http://localhost:5173/escola/escola-piloto/login`

- [ ] A escola aparece **fixada** (com ícone de escolinha), **sem** dropdown — não pode ser alterada
- [ ] Login funciona normalmente

### 2.3 Slug inexistente

1. Abrir `http://localhost:5173/escola/escola-fictícia-xyz/login`

- [ ] Mensagem de erro: `Escola "escola-fictícia-xyz" não encontrada. Seleccione uma escola disponível.`
- [ ] Dropdown reaparece para o user poder escolher

### 2.4 Cross-tenant (criar 2ª escola via admin)

1. Login como `admin / admin123`
2. Em alguma página de gestão de escolas, criar nova escola **com tenant** (ou via `POST /api/v1/escolas/with-tenant` directo)
3. Voltar à página de login pública

- [ ] `GET /api/v1/auth/tenants` (curl) devolve as 2 escolas
- [ ] No dropdown da página de login, a nova escola aparece
- [ ] O slug é gerado automaticamente em formato `kebab-case` ASCII (ex: `Escola Mutu Ya Kevela` → `escola-mutu-ya-kevela`)

---

## 3. Portal Direcção / Secretaria (`/gestao`)

> Login: `diretor / diretor123` ou `admin / admin123`

### 3.1 Dashboard Direcção (#44, #45)

1. Aceder a `/gestao` (rota inicial)

- [ ] **8 cards** com totais reais: Alunos (100), Activos (100), Professores (15), Encarregados (80), Turmas (6), Disciplinas (24), Avaliações Lançadas, Matrículas Pendentes
- [ ] Secção **"Matrículas por Estado"** com barra horizontal colorida (verde/laranja/vermelho)
- [ ] Legenda em baixo mostra contagens absolutas + percentagens
- [ ] Sem cards a "0" indevidamente (se aparecer 0, verificar seed)

### 3.2 Lista de Escolas (super_admin only)

> Apenas visível como `admin`.

- [ ] Lista mostra a "Escola Piloto SIENA" + qualquer outra que tenhas criado
- [ ] Botão "Nova Escola" abre formulário com tenant + diretor

### 3.3 Alunos — Lista, Criação, Edição

1. Sidebar → "Alunos"

- [ ] Tabela com 100 alunos, paginação no rodapé (`total: 100`, primeira página com 50)
- [ ] Pesquisa por nome/BI funciona
- [ ] Botão "Novo Aluno" abre formulário

#### 3.3.1 Criar aluno SEM encarregado vinculado (Tasks #36)

1. Botão "Novo Aluno"
2. Preencher dados pessoais. **Não** seleccionar encarregado.

- [ ] No fim do form aparece secção **"Vincular a encarregado (opcional)"** com EntitySelect, dropdown de relação e checkbox "Encarregado principal"
- [ ] Submeter cria aluno com `HTTP 201`
- [ ] Aluno aparece na lista

#### 3.3.2 Criar aluno COM encarregado já vinculado

1. Repetir, agora seleccionar um encarregado no EntitySelect (com pesquisa por nome)
2. Escolher relação "Pai" e marcar "Principal"

- [ ] EntitySelect mostra resultados ao pesquisar (ex: digitar "Manuel")
- [ ] Após guardar, o aluno aparece com vínculo (validar via `GET /api/v1/alunos/{id}/encarregados`)

### 3.4 Encarregados — Lista, Criação com vínculo (#35)

1. Sidebar → "Encarregados"

- [ ] Tabela com 80 encarregados
- [ ] Botão "Novo Encarregado"

#### 3.4.1 Criar encarregado COM aluno vinculado

1. Preencher dados pessoais
2. Na secção **"Vincular a aluno (opcional)"**, escolher aluno via EntitySelect
3. Relação: "Pai", marcar "Principal"

- [ ] Form submete sem erros
- [ ] `GET /api/v1/alunos/{aluno_id}/encarregados` devolve o novo encarregado

### 3.5 Turmas — Lista, Criação, Detalhe

1. Sidebar → "Turmas"

- [ ] Tabela com 6 turmas (7.ª-A, 7.ª-B, 8.ª-A, 8.ª-B, 9.ª-A, 9.ª-B)
- [ ] Coluna "Professor Regente" mostra **nome** (não UUID)

#### 3.5.1 Criar turma com EntitySelect de regente (#29)

1. Botão "Nova Turma"

- [ ] Campo "Professor Regente" é **EntitySelect** (botão clicável, não dropdown nativo)
- [ ] Ao clicar, abre popup com pesquisa por nome + lista debounced (250ms)
- [ ] Cada item mostra nome + código funcional + especialidade

#### 3.5.2 Detalhe da turma

1. Clicar "Ver" numa turma

- [ ] Mostra info: regente, ano lectivo, classe, turno, sala, capacidade
- [ ] Lista de horários (5 dias × ~6 slots) com disciplina e professor por **nome**

### 3.6 Matrículas — Lista, Criação, Validação (#27, #28, #24)

1. Sidebar → "Matrículas"

- [ ] Tabela com 100 matrículas (estado: aprovada)
- [ ] Coluna "Aluno" mostra **nome + nº processo** (não UUID)
- [ ] Tabs: Todas / Pendentes / Aprovadas / Rejeitadas — filtro funciona

#### 3.6.1 Criar matrícula COM aluno que tem encarregado

1. "Nova Matrícula"
2. Campo "Aluno" é EntitySelect com pesquisa
3. Campo "Ano Lectivo" é dropdown simples
4. Escolher aluno do seed (todos têm encarregado), classe, turno

- [ ] Submeter retorna `HTTP 201` e a matrícula aparece em "Pendentes"
- [ ] Botões ✓/✗ permitem aprovar/rejeitar

#### 3.6.2 Validação: aluno SEM encarregado (Task #24) — **caminho de erro**

1. Criar primeiro um aluno **sem** encarregado vinculado (3.3.1)
2. Tentar criar matrícula desse aluno

- [ ] Resposta `HTTP 422`
- [ ] Mensagem visível na UI: `"Aluno não tem encarregado de educação vinculado — registe pelo menos 1 encarregado antes de criar matrícula"`

### 3.7 Horários — Criar aula (#34)

1. Sidebar → "Horários"
2. Seleccionar uma turma, clicar "Adicionar Aula"

- [ ] Campo "Disciplina" é EntitySelect (pesquisa por nome ou código)
- [ ] Campo "Professor" é EntitySelect (pesquisa por nome)
- [ ] Após submeter, a aula aparece na grelha semanal com nome da disciplina + professor

### 3.8 Pauta da Turma (#43)

1. Pauta da Turma (rota `/gestao/pauta` ou similar)

- [ ] Selector de turma + selector de período (1/2/3)
- [ ] Tabela: linhas = alunos, colunas = disciplinas, células = média por disciplina
- [ ] Última coluna: média geral por aluno
- [ ] Médias com cores semáforo (verde ≥10, vermelho <10)

---

## 4. Portal Professor (`/professor`)

> Login: `professor / professor123`

### 4.1 Dashboard Professor (#46)

1. Aceder a `/professor`

- [ ] Saudação: `Bem-vindo, Prof. <nome real>` (não username)
- [ ] **4 cards**: Turmas Atribuídas, Disciplinas que Lecciona, Total Alunos, Notas por Lançar
- [ ] Tabela **"Minhas Turmas"** com colunas: Turma, Classe, Turno, Disciplinas, Alunos, Regência (estrela amarela se regente)
- [ ] Tabela **"Próximas Aulas"** com Dia, Hora, Turma, Disciplina

### 4.2 Lançar Notas — Cascata Turma → Disciplina → Alunos (#31, #32, #33)

1. Sidebar → "Lançar Notas"

- [ ] Dropdown "Turma" mostra **apenas as turmas do professor** (não todas)
- [ ] Antes de escolher turma, dropdown "Disciplina" está **desabilitado** com texto "Seleccione primeiro a turma"

#### 4.2.1 Cascata em acção

1. Escolher uma turma
2. Observar campo Disciplina

- [ ] Dropdown "Disciplina" agora habilitado com **apenas disciplinas que o prof dá nessa turma**
- [ ] Se o prof não dá nenhuma disciplina nesta turma (regente sem aulas), mostra "Sem disciplinas nesta turma"

#### 4.2.2 Criar Avaliação

1. Escolher turma + disciplina, "Nova Avaliação"

- [ ] Form pré-preenchido com a turma + disciplina seleccionadas
- [ ] Tipo, Período, Data, Peso, Nota Máxima editáveis

#### 4.2.3 Lançar Notas — sem dropdown manual de aluno

1. Numa avaliação criada, "Lançar Notas"

- [ ] Página mostra **tabela com TODOS os alunos da turma** (não dropdown)
- [ ] Cada linha tem: Nome, Nº Processo, input "Nota", input "Observações"
- [ ] Cabeçalho mostra `"X aluno(s) na turma"`
- [ ] Submeter envia só linhas com nota preenchida (linhas em branco são ignoradas)

### 4.3 Meu Horário

1. Sidebar → "Meu Horário"

- [ ] Grelha semanal com aulas próprias
- [ ] Cada célula mostra disciplina + turma

### 4.4 Minhas Turmas

1. Sidebar → "Minhas Turmas"

- [ ] Lista de turmas onde lecciona OU é regente
- [ ] Detalhe: lista de alunos da turma, com nome + nº processo

---

## 5. Portal Aluno (`/aluno`)

> Login: `aluno / aluno123`

### 5.1 Dashboard Aluno (#47)

1. Aceder a `/aluno`

- [ ] Saudação: `Olá, <nome real>` + linha com nº processo, classe, turma
- [ ] **4 cards**: Média Geral (com 2 decimais), Faltas Total, Faltas Injustificadas, Próximas Avaliações
- [ ] Secção **"Resumo por Disciplina"**: tabela com disciplina, média (badge verde/vermelho), faltas (✓ verde se 0)
- [ ] Secção **"Próximas Avaliações"**: tabela com data, disciplina, tipo, nota máxima

### 5.2 Boletim (#51)

1. Sidebar → "Boletim"

- [ ] Tabs: 1.º / 2.º / 3.º Período
- [ ] Tabela: disciplina, média (badge cor semáforo), faltas
- [ ] No fim, **"Média do período"** com badge

### 5.3 Minhas Faltas (#52)

1. Sidebar → "Minhas Faltas"

- [ ] 3 cards: Total / Justificadas / Injustificadas
- [ ] Tabs de filtro: Todas / Justificadas / Injustificadas
- [ ] Tabela: data, disciplina (nome, não UUID), turma, tipo (badge), justificativa

### 5.4 Horário Aluno (#53)

1. Sidebar → "Horário"

- [ ] Grelha semanal com **todas** as aulas da turma
- [ ] Cada célula tem disciplina (nome real) + professor (nome real)
- [ ] Sem células vazias com UUIDs truncados

---

## 6. Portal Encarregado (`/encarregado`)

> Login: `encarregado / encarregado123`

### 6.1 Lista de Educandos (#48)

1. Aceder a `/encarregado`

- [ ] Saudação com nome do encarregado + contagem de educandos
- [ ] **Cards de educandos** (1 por aluno vinculado), cada um mostra: nome, classe, turma, média, faltas
- [ ] Card seleccionado tem moldura azul (#1A3F7A)
- [ ] Clicar num card muda o educando seleccionado

### 6.2 Resumo do Educando (Tab "Resumo")

1. Seleccionar um educando, tab "Resumo"

- [ ] Linha com nº processo + classe/turma
- [ ] 4 cards: Média Geral, Total Faltas, Faltas Injustificadas, Próximas Avaliações

### 6.3 Boletim do Educando (Tab "Boletim", #49)

1. Tab "Boletim"

- [ ] Tabs de período (1/2/3)
- [ ] Tabela: disciplina, média (badge cor), faltas

### 6.4 Faltas do Educando (Tab "Faltas", #50)

1. Tab "Faltas"

- [ ] Tabela: data, disciplina, tipo (badge), justificativa
- [ ] Sem UUIDs visíveis nem dados em falta

---

## 7. Validações Cross-Cutting

### 7.1 Tenant Isolation

> Login num tenant deve ver **apenas** dados desse tenant.

1. Login como `admin / admin123` (tenant: escola-piloto)
2. Listar alunos: `curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/alunos`
3. Login como diretor da 2ª escola (se criada em 2.4)
4. Listar alunos no mesmo endpoint

- [ ] Tenant 1 vê 100 alunos
- [ ] Tenant 2 vê 0 alunos (escola nova, sem seed)
- [ ] Tentar `GET /api/v1/alunos/<id_de_tenant_1>` no tenant 2 → **HTTP 404**

### 7.2 Identidades derivadas no `/auth/me`

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"tenant_slug":"escola-piloto","username":"professor","password":"professor123"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/auth/me | python3 -m json.tool
```

- [ ] Resposta inclui `professor_id` não-nulo
- [ ] `aluno_id` e `encarregado_id` são `null`
- [ ] Repetir com `aluno`: `aluno_id` não-nulo, restantes null
- [ ] Repetir com `encarregado`: `encarregado_id` não-nulo, restantes null
- [ ] Repetir com `admin`: todos os 4 IDs derivados são `null` (admin não tem pessoa)

### 7.3 Paginação

```bash
curl -s -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/alunos?limit=5&offset=10" \
  | python3 -m json.tool | head -20
```

- [ ] Resposta tem `total: 100, offset: 10, limit: 5, items: [5 items]`
- [ ] `total` mantém-se 100 mesmo com offset/limit diferentes
- [ ] Filtro: `/matriculas?estado=pendente` → `total` reflecte só pendentes (0 no seed)

### 7.4 Componente EntitySelect

> Validar nos 5 sítios onde aparece: Matrículas, Turmas, Horários, Encarregados (vincular aluno), Alunos (vincular encarregado).

- [ ] Click → popup abre com input de pesquisa em foco
- [ ] Escrever "Manuel" → resultados filtram em ~250ms (debounce visível)
- [ ] Selecção mostra label no botão e o popup fecha
- [ ] Botão `X` à direita limpa a selecção
- [ ] Click fora do popup fecha-o
- [ ] Required: tentar submeter form sem seleccionar → form não submete

---

## 8. Endpoints API Críticos (smoke tests)

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"tenant_slug":"escola-piloto","username":"admin","password":"admin123"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
H="Authorization: Bearer $TOKEN"

# Sprint 2 endpoints
curl -s -H "$H" http://localhost:8000/api/v1/turmas/lookup | python3 -m json.tool | head -10
TURMA=$(curl -s -H "$H" http://localhost:8000/api/v1/turmas/lookup | python3 -c "import sys,json;print(json.load(sys.stdin)[0]['id'])")
curl -s -H "$H" "http://localhost:8000/api/v1/turmas/$TURMA/alunos" | python3 -c "import sys,json;d=json.load(sys.stdin);print(f'{len(d)} alunos na turma')"

PROF=$(curl -s -H "$H" http://localhost:8000/api/v1/professores/lookup | python3 -c "import sys,json;print(json.load(sys.stdin)[0]['id'])")
curl -s -H "$H" "http://localhost:8000/api/v1/professores/$PROF/turmas" | python3 -c "import sys,json;d=json.load(sys.stdin);print(f'{len(d)} turmas atribuidas')"
curl -s -H "$H" "http://localhost:8000/api/v1/professores/$PROF/disciplinas" | python3 -c "import sys,json;d=json.load(sys.stdin);print(f'{len(d)} disciplinas que lecciona')"

# Sprint 3 endpoints
curl -s -H "$H" http://localhost:8000/api/v1/dashboard/gestao | python3 -m json.tool
curl -s -H "$H" "http://localhost:8000/api/v1/dashboard/professor?professor_id=$PROF" | python3 -c "import sys,json;d=json.load(sys.stdin);print(f'Prof {d[\"nome\"]}: {d[\"turmas_atribuidas\"]} turmas, {d[\"disciplinas_lecciona\"]} disciplinas')"
curl -s -H "$H" "http://localhost:8000/api/v1/turmas/$TURMA/pauta?periodo=1" | python3 -c "import sys,json;d=json.load(sys.stdin);print(f'Pauta: {len(d[\"linhas\"])} alunos x {len(d[\"disciplinas\"])} disciplinas')"
```

- [ ] Todos os endpoints respondem `HTTP 200`
- [ ] Contagens fazem sentido (turma com 16-17 alunos, prof com 1-5 turmas, etc.)

---

## 9. Bugs Encontrados

> Anota aqui qualquer comportamento inesperado durante o teste. Format livre.

```
- [ ] (data) Página X: bug Y. Reprodução: ...
```

---

## 10. Checklist de Conclusão

Após percorrer todas as secções 1–8:

- [ ] Sprint 0 (multi-tenant) — 4/4 secções OK
- [ ] Sprint 1 (DTOs enriquecidos) — visível em todas as tabelas (sem UUIDs)
- [ ] Sprint 2 (dropdowns + cascata) — EntitySelect em 5 páginas + LancarNotas em cascata
- [ ] Sprint 3 (dashboards) — 4 portais com cards + tabelas reais
- [ ] Validações cross-cutting (secção 7) — tenant isolation, /auth/me, paginação, EntitySelect
- [ ] API smoke tests (secção 8) — todos os endpoints respondem

**Quando todos passarem, a Fase 1.1 (Sprints 1–3) está validada e pronta para o Sprint 4 (Portal Admin).**
