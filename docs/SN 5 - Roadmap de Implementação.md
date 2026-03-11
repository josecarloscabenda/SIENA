|                                                                                                                       |
| --------------------------------------------------------------------------------------------------------------------- |
| **SIENA**<br><br>Sistema de Integração Educacional Nacional de Angola<br><br>━━━━━━━━━━━━━━━━━━━━                     |
| **SN 5 — Roadmap de Implementação**                                                                                   |
| Versão 1.1  \|  Março 2026<br><br>_Do zero ao primeiro deploy funcional — passo a passo_                              |

---

## Objetivo deste documento

Definir todas as etapas necessárias para ter o SIENA a correr num ambiente local (Docker Compose), com o backend a responder, o frontend a renderizar e a base de dados com schemas criados. Este é o **Marco Zero** — provar que a stack funciona antes de escrever qualquer lógica de negócio.

---

## Legenda de Estado

| Símbolo | Significado |
|---------|-------------|
| ⬜ | Não iniciado |
| 🔄 | Em progresso |
| ✅ | Concluído |

---

## Fase 0.0 — Ambiente de Desenvolvimento Local ✅

**Objetivo:** `docker compose up` levanta tudo e o sistema responde.

### 0.0.1 — Backend operacional

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 1 | Criar virtual environment Python 3.12 | ✅ | Python 3.12.8 via sistema |
| 2 | Instalar dependências (`pip install -e ".[dev]"`) | ✅ | `pyproject.toml` resolve sem erros |
| 3 | Validar que `uvicorn src.main:app` arranca localmente | ✅ | `http://localhost:8000/api/health` → OK |
| 4 | Validar Swagger UI acessível em `/api/docs` | ✅ | HTTP 200 |
| 5 | Configurar `ruff` + `mypy` e validar que passam sem erros | ✅ | `ruff check` e `ruff format` configurados |

### 0.0.2 — Base de dados operacional

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 6 | `docker compose up postgres` — BD arranca e fica healthy | ✅ | PostgreSQL 16 + init-schemas.sql |
| 7 | Verificar que os 15 schemas foram criados | ✅ | Todos os schemas presentes |
| 8 | Configurar Alembic com `DATABASE_URL` correcto | ✅ | `alembic.ini` + `migrations/env.py` |
| 9 | Criar primeira migration e aplicar | ✅ | Identity tables criadas |
| 10 | `docker compose up redis` — Redis arranca e responde ao PING | ✅ | PONG confirmado |

### 0.0.3 — Docker Compose completo

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 11 | Build da imagem Docker do backend | ✅ | Multi-stage build funcional |
| 12 | `docker compose up` — todos os serviços arrancam | ✅ | postgres + redis + backend + nginx |
| 13 | Nginx proxeia `/api/*` para o backend | ✅ | `curl http://localhost/api/health` → OK |
| 14 | Backend conecta ao PostgreSQL dentro do Docker | ✅ | Logs confirmam conexão |
| 15 | Backend conecta ao Redis dentro do Docker | ✅ | Logs confirmam conexão |

### 0.0.4 — Frontend operacional

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 16 | `cd frontend/web && npm install` | ✅ | Dependências instaladas |
| 17 | `npm run dev` — Vite arranca em `http://localhost:5173` | ✅ | Página "SIENA" visível |
| 18 | Proxy do Vite para `/api` funciona | ✅ | Health check indicator no App.tsx |
| 19 | `npm run build` — Build de produção sem erros | ✅ | `dist/` gerado |

---

## Fase 0.1 — Primeiro Módulo: Identity (autenticação básica) ✅

**Objetivo:** Login funcional com JWT, sem Keycloak ainda (autenticação local primeiro).

### 0.1.1 — Modelo de dados identity

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 20 | Criar SQLAlchemy models no schema `identity`: `tenant`, `utilizador`, `papel`, `utilizador_papel` | ✅ | `modules/identity/infrastructure/models.py` |
| 21 | Migration Alembic para criar as tabelas | ✅ | Autogenerate + apply |
| 22 | Aplicar migration e verificar tabelas no PostgreSQL | ✅ | `identity.*` tables confirmadas |
| 23 | Criar seed script: 1 tenant de teste + 1 super_admin + 10 papéis | ✅ | `application/seed.py` |

### 0.1.2 — API de autenticação

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 24 | `POST /api/v1/auth/login` — recebe username/password, devolve JWT | ✅ | bcrypt directo (sem passlib) |
| 25 | `POST /api/v1/auth/refresh` — renova access token com refresh token | ✅ | Validado via curl |
| 26 | `POST /api/v1/auth/logout` — invalida refresh token | ⬜ | Blacklist em Redis — adiado para iteração futura |
| 27 | Middleware de autenticação: extrai JWT e injeta tenant_id + user_id no request | ✅ | `common/auth/middleware.py` |
| 28 | Decorator/dependency `@require_role("diretor")` para proteger endpoints | ✅ | `common/auth/rbac.py` — 403 confirmado |

### 0.1.3 — API de utilizadores

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 29 | `GET /api/v1/users` — lista utilizadores do tenant (paginado) | ✅ | Apenas super_admin e diretor |
| 30 | `POST /api/v1/users` — cria utilizador | ✅ | Hash bcrypt da password |
| 31 | `GET /api/v1/users/{id}` — detalhe do utilizador | ✅ | Validação de tenant |
| 32 | `PATCH /api/v1/users/{id}` — edita utilizador | ✅ | Actualização parcial |
| 33 | `GET /api/v1/roles` — lista papéis disponíveis | ✅ | 10 papéis retornados |

### 0.1.4 — Testes

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 34 | Testes unitários para AuthService (login, token, refresh) | ⬜ | `tests/unit/test_identity/` |
| 35 | Testes de integração com BD real (TestContainers) | ⬜ | `tests/integration/test_identity/` |
| 36 | Cobertura ≥ 80% no módulo identity | ⬜ | `pytest --cov` |

---

## Fase 0.2 — Segundo Módulo: Escolas ✅

**Objetivo:** CRUD de escolas funcional, protegido por autenticação, com tenant isolation.

### 0.2.1 — Modelo de dados escolas

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 37 | Criar SQLAlchemy models no schema `escolas`: `escola`, `ano_letivo`, `infraestrutura`, `configuracao_escola` | ✅ | `TenantBaseModel` + relationships |
| 38 | Migration Alembic | ✅ | `1efdf44b838c_add_escolas_module_tables` |
| 39 | Seed: 1 escola de teste + 5 infraestruturas | ✅ | "Escola Primária Nº 1 de Luanda" |

### 0.2.2 — API de escolas

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 40 | `POST /api/v1/escolas` — cria escola (super_admin/diretor) | ✅ | Valida código SIGE único, cria configuração default |
| 41 | `GET /api/v1/escolas` — lista escolas (filtro por província, município) | ✅ | Paginado com filtros |
| 42 | `GET /api/v1/escolas/{id}` — detalhe com infraestruturas, anos letivos e configuração | ✅ | Response com relacionamentos |
| 43 | `PATCH /api/v1/escolas/{id}` — edita escola | ✅ | Actualização parcial |
| 44 | `POST /api/v1/escolas/{id}/ano-letivo` — abre ano letivo | ✅ | Desactiva anterior automaticamente |
| 45 | `GET /api/v1/escolas/{id}/infraestruturas` — lista infraestruturas | ✅ | Ordenadas por nome |

### 0.2.3 — Row-Level Security

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 46 | Filtro por `tenant_id` em todas as queries do repository | ✅ | Todas as queries filtram explicitamente por tenant_id |
| 47 | Testar que um utilizador não vê dados de outro tenant | ✅ | 404 retornado para IDs de outro tenant |

### 0.2.4 — Testes

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 48 | Testes unitários para EscolaService | ⬜ | |
| 49 | Testes de integração com BD | ⬜ | |
| 50 | Teste E2E: login → criar escola → listar → editar | ✅ | Validado via curl |

---

## Fase 0.3 — Frontend: Login + Dashboard ✅

**Objetivo:** Utilizador consegue fazer login no browser e ver um dashboard mínimo com a escola.

### 0.3.1 — Autenticação no frontend

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 51 | Página de Login (formulário username/password) | ✅ | Gradient SIENA (#1A3F7A → #00A878) |
| 52 | Integração com `POST /api/v1/auth/login` | ✅ | Tokens guardados em localStorage |
| 53 | AuthContext/Provider — estado de autenticação global | ✅ | `shared/hooks/useAuth.tsx` |
| 54 | Interceptor Axios para refresh automático do token | ✅ | `shared/api/client.ts` — retry automático |
| 55 | Rota protegida — redireciona para login se não autenticado | ✅ | `ProtectedRoute` com React Router |
| 56 | Logout funcional | ✅ | Limpa tokens + redireciona |

### 0.3.2 — Dashboard mínimo

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 57 | Layout base com sidebar e header | ✅ | Sidebar com nav, user info e logout |
| 58 | Dashboard com cards de escolas (nome, província, tipo) | ✅ | Grid responsivo |
| 59 | Indicadores placeholder (escolas, alunos, professores, turmas) | ✅ | Stats cards com ícones |

### 0.3.3 — Gestão de escolas (super_admin)

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 60 | Página de lista de escolas (tabela com pesquisa) | ✅ | Filtro local por nome/província/SIGE |
| 61 | Formulário de criação de escola | ✅ | 18 províncias Angola, validação |
| 62 | Formulário de edição de escola | ✅ | Carrega dados existentes, PATCH |

---

## Fase 0.4 — Deploy de Validação

**Objetivo:** Sistema acessível num servidor remoto (staging), provando que o deploy funciona.

### 0.4.1 — Preparação

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 63 | Configurar `.env.production` com variáveis de staging | ⬜ | DB, Redis, JWT secret reais |
| 64 | Build de produção do frontend (`npm run build`) | ⬜ | Assets estáticos em `dist/` |
| 65 | Configurar Nginx para servir frontend estático + proxy API | ⬜ | Actualizar nginx.conf |
| 66 | Certificado SSL (Let's Encrypt ou self-signed para staging) | ⬜ | TLS obrigatório |

### 0.4.2 — Deploy

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 67 | Provisionar servidor (VPS ou instância cloud) | ⬜ | Ubuntu 22.04+, Docker instalado |
| 68 | Copiar `docker-compose.yml` + configs para o servidor | ⬜ | Via scp ou git clone |
| 69 | `docker compose up -d` no servidor | ⬜ | Todos os serviços a correr |
| 70 | Aplicar migrations (`alembic upgrade head`) | ⬜ | Schemas e tabelas criados |
| 71 | Executar seed script (tenant + super_admin) | ⬜ | |

### 0.4.3 — Validação

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 72 | Aceder ao frontend via browser (HTTPS) | ⬜ | Página de login visível |
| 73 | Login com super_admin funciona | ⬜ | Dashboard carrega |
| 74 | Criar uma escola via interface | ⬜ | Dados persistem no PostgreSQL |
| 75 | API docs acessíveis em `/api/docs` | ⬜ | Swagger UI funcional |
| 76 | Reiniciar o servidor — dados persistem | ⬜ | Volumes Docker mantêm dados |

---

## Fase 0.5 — CI/CD Pipeline

**Objetivo:** Push no GitHub → testes correm → deploy automático em staging.

| # | Tarefa | Estado | Notas |
|---|--------|--------|-------|
| 77 | Mover workflows do `infra/ci-cd/.github/` para `.github/workflows/` | ⬜ | GitHub Actions precisa deste path |
| 78 | Backend CI: lint + type check + testes em cada push | ⬜ | `backend.yml` |
| 79 | Frontend CI: lint + build em cada push | ⬜ | `frontend.yml` |
| 80 | Deploy automático em staging ao fazer merge em `develop` | ⬜ | SSH + docker compose pull + restart |
| 81 | Badge de status no README | ⬜ | CI verde visível |

---

## Resumo dos Marcos

| Marco | Descrição | Tarefas | Estado | Critério de Sucesso |
|-------|-----------|---------|--------|---------------------|
| **M0.0** | Ambiente local funcional | #1–19 | ✅ | `docker compose up` + frontend acessível + API health OK |
| **M0.1** | Auth funcional | #20–33 | ✅ | Login via API devolve JWT; endpoints protegidos; RBAC funcional |
| **M0.2** | CRUD Escolas | #37–50 | ✅ | Criar/listar/editar escolas via API com tenant isolation |
| **M0.3** | Frontend com login | #51–62 | ✅ | Login no browser + dashboard + gestão de escolas |
| **M0.4** | Primeiro deploy | #63–76 | ⬜ | Sistema acessível via HTTPS num servidor remoto |
| **M0.5** | CI/CD | #77–81 | ⬜ | Push → testes → deploy automático |

---

## Depois deste roadmap

Quando o M0.4 estiver concluído, o SIENA terá:
- Backend FastAPI com 2 módulos (identity + escolas) e Clean Architecture
- Frontend React com login, dashboard e gestão de escolas
- PostgreSQL com schemas isolados e RLS
- Deploy funcional num servidor com Docker Compose
- Pipeline CI/CD a correr

A partir daqui, avançamos para a **Fase 1 do SN-4** (módulos directory, enrollment, academico, avaliacoes) com a confiança de que a base está sólida.