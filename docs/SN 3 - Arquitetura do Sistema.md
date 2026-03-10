|                                                                                                                       |
| --------------------------------------------------------------------------------------------------------------------- |
| **SIENA**<br><br>Sistema de Integração Educacional Nacional de Angola<br><br>━━━━━━━━━━━━━━━━━━━━                     |
| **SN 3 — Arquitetura do Sistema**                                                                                     |
| Versão 3.0  \|  Março 2026<br><br>_Monólito Modular com Clean Architecture  \|  Backend: Python/FastAPI  \|  Frontend: React 18_ |

**1. Visão Geral da Arquitetura**

**O SIENA adota uma arquitetura de monólito modular com Clean Architecture desde o início. Cada domínio de negócio é um módulo independente dentro de uma única aplicação, com o seu próprio schema PostgreSQL, fronteiras claras e isolamento lógico. Esta abordagem garante simplicidade operacional na fase inicial, com evolução faseada para microserviços quando a escala nacional o justificar.**



|   |   |
|---|---|
|**Decisão Arquitectural**|**Valor**|
|Padrão|Monólito Modular (Domain-Driven Design + Clean Architecture)|
|Estratégia de evolução|Módulos extraíveis para microserviços de forma faseada, quando o volume justificar|
|Topologia|Híbrida: admin local (offline-ready) + portais e serviços na nuvem|
|Backend|Python 3.12 + FastAPI (async, OpenAPI nativo) — aplicação única com módulos por domínio|
|Frontend|React 18 + TypeScript (Vite, SPA + SSR quando necessário)|
|Mobile|React Native (portais simplificados para alunos/encarregados)|
|API externa|REST/JSON via Nginx reverse proxy|
|Comunicação interna|Import direto entre módulos (in-process); eventos internos para desacoplamento|
|Comunicação assíncrona|RabbitMQ (integrações externas e sincronização offline)|
|Base de dados|PostgreSQL 16 único com schemas por módulo + Redis (cache, sessões)|
|Autenticação|Keycloak (OIDC/OAuth2, SSO, MFA)|
|Infraestrutura|Docker Compose (dev/staging); evolução para Kubernetes quando a escala justificar|
|Observabilidade|Prometheus + Grafana + OpenTelemetry (logs JSON)|
|CI/CD|GitHub Actions, semver, feature flags|

**2. Justificação: Monólito Modular vs. Microserviços**

**2.1 Por que não microserviços desde o início?**

**A arquitetura de microserviços com base de dados por serviço é a meta a longo prazo, mas implementá-la desde o início apresenta riscos e custos desproporcionais para a fase atual do projeto:**

|   |   |
|---|---|
|**Aspecto**|**Impacto de 15 microserviços na fase piloto**|
|Custo de infraestrutura|15 instâncias PostgreSQL = $1.500–2.400/mês vs. $150–300/mês com BD única|
|Complexidade operacional|15 pipelines CI/CD, 15 conjuntos de migrations, 15 ciclos de versioning|
|Queries cross-domínio|Gerar um boletim escolar requer dados de 4 serviços via REST; com BD única é um JOIN|
|Consistência|Outbox Pattern + DLQ entre 15 serviços é difícil de debugar com equipa pequena|
|Equipa|5–6 pessoas não conseguem operar 15 serviços independentes de forma eficiente|



**2.2 O que o monólito modular preserva**

- **Mesmas fronteiras de domínio** — cada módulo tem a mesma separação lógica que teria como microserviço;
- **Mesmo contrato de API** — os endpoints REST são idênticos (/api/v1/escolas, /api/v1/enrollment);
- **Isolamento de dados** — schemas PostgreSQL separados por módulo, com RLS para multi-tenancy;
- **Clean Architecture interna** — cada módulo segue api/domain/application/infrastructure;
- **Evolução garantida** — quando um módulo precisar de escala independente, extrai-se para um serviço sem alterar a API.



**2.3 Plano de Evolução Faseada**

|   |   |   |
|---|---|---|
|**Fase**|**Escala**|**Arquitetura**|
|Piloto|1–3 escolas|Monólito modular, PostgreSQL único com schemas, Docker Compose|
|Expansão|50–200 escolas|Extrair módulos de alta carga (avaliacoes, relatorios) para serviços independentes; introduzir Redis e RabbitMQ para eventos|
|Nacional|1.000+ escolas|Microserviços por domínio com DBs separadas onde o volume justifica; Kubernetes com HPA|

**3. Princípios Arquiteturais**

**3.1 Isolamento por Domínio (Módulos)**

**Cada módulo possui o seu próprio schema PostgreSQL dentro da mesma instância. Nenhum módulo acede diretamente às tabelas de outro. A comunicação entre módulos é feita via serviços de aplicação (import direto in-process) ou eventos internos para operações assíncronas.**

- Schema per module: isolamento lógico de dados sem custo de infraestrutura adicional;
- Bounded contexts claros: cada módulo encapsula a sua lógica de domínio;
- Fronteiras explícitas: cada módulo expõe uma interface pública (services/DTOs) para comunicação com outros módulos;
- Deploy único: simplifica operações, CI/CD e monitorização;
- Extraível: qualquer módulo pode tornar-se um microserviço movendo-o para o seu próprio processo e substituindo imports por chamadas REST.



**3.2 Multi-Tenant por Escola**

**O sistema é multi-tenant desde a base. Cada escola é um tenant isolado. O isolamento é garantido em múltiplas camadas:**

- tenant_id obrigatório em todas as tabelas de todos os schemas;
- Row-Level Security (RLS) ativo no PostgreSQL;
- Middleware FastAPI valida o tenant em cada request;
- Tokens JWT incluem tenant_id — sem possibilidade de escapes entre escolas.



**3.3 Offline-First para Administração Local**

**Muitas escolas angolanas operam com conectividade instável. O módulo administrativo local (secretaria, diretor) funciona offline com sincronização assíncrona para a nuvem:**

- SQLite local + agente de sincronização (Python);
- Outbox Pattern: operações gravadas localmente antes de serem enviadas;
- Delta sync: apenas as alterações desde a última sincronização são transmitidas;
- Conflict resolution: política Last-Write-Wins (LWW) + revisão manual para entidades críticas (notas, matrículas);
- Transporte HTTPS com assinatura HMAC por tenant.



**3.4 Segurança em Profundidade**

- Autenticação centralizada via Keycloak (OIDC/OAuth2);
- JWT com expiração curta (access token: 15 min; refresh token: 7 dias);
- MFA obrigatório para perfis administrativos;
- RBAC fino: permissões por papel (diretor, secretaria, professor...) e escopo (escola/turma);
- Encriptação TLS 1.3 em trânsito, AES-256 em repouso;
- Auditoria imutável de todas as operações sensíveis;
- Secrets geridos em variáveis de ambiente seguras (dotenv/Vault), nunca em código ou BD.



**3.5 Observabilidade**

- Logs JSON estruturados em toda a aplicação (correlationId por request);
- Métricas expostas via /metrics (Prometheus scraping);
- Dashboards Grafana por módulo e por nível de negócio;
- Tracing com OpenTelemetry (rastreio de requests entre módulos);
- Alertas automáticos: latência, taxa de erro, saturation, tráfego.

**4. Diagrama de Componentes (Descritivo)**

**O sistema é composto pelas seguintes camadas lógicas:**



**4.1 Camada de Acesso (Portais e Apps)**

|   |   |   |   |
|---|---|---|---|
|**Portal / App**|**Tecnologia**|**Utilizadores**|**Hospedagem**|
|Portal Web (SPA)|React 18 + TypeScript (Vite)|Todos os perfis|CDN (Cloudflare/AWS CloudFront)|
|Admin Local (Offline)|React + Tauri|Secretaria, Diretor|Instalado localmente na escola|
|App Mobile|React Native|Alunos, Encarregados|App Store / APK distribuído|
|Portal ANEP|React 18 (instância separada)|ANEP, Gestores de concursos|CDN|



**4.2 Camada de Reverse Proxy**

**Ponto único de entrada para todos os clientes. Implementado com Nginx.**

|   |   |
|---|---|
|**Responsabilidade**|**Detalhe**|
|Roteamento|Encaminha requests para a aplicação FastAPI|
|Autenticação|Validação JWT delegada à aplicação (middleware FastAPI)|
|Rate Limiting|Por tenant e por IP (proteção contra abuso e DoS)|
|SSL Termination|TLS 1.3 termina no Nginx|
|Logging|Registo de todos os requests (método, path, status, latência)|



**4.3 Camada de Aplicação (Backend Python/FastAPI)**

**Aplicação única com módulos independentes. Todos os módulos partilham a mesma estrutura interna (Clean Architecture):**

```
backend/
├── src/
│   ├── common/                    # Código partilhado
│   │   ├── auth/                  # JWT validation, RBAC helpers, tenant middleware
│   │   ├── database/              # SQLAlchemy base, session factory, mixins (tenant, audit, timestamps)
│   │   ├── events/                # Event bus interno (in-process pub/sub)
│   │   ├── schemas/               # Pydantic schemas comuns (pagination, errors, responses)
│   │   └── utils/                 # Helpers, logging config, error handling
│   │
│   ├── modules/
│   │   ├── identity/              # Auth, RBAC, SSO, licenças
│   │   │   ├── api/               # Routers FastAPI, DTOs Pydantic
│   │   │   ├── domain/            # Entidades, value objects, regras de negócio
│   │   │   ├── application/       # Use cases / serviços de aplicação
│   │   │   └── infrastructure/    # Repositórios SQLAlchemy, adaptadores Keycloak
│   │   ├── escolas/               # (mesma estrutura interna)
│   │   ├── directory/
│   │   ├── enrollment/
│   │   ├── academico/
│   │   ├── avaliacoes/
│   │   ├── financeiro/
│   │   ├── provas/
│   │   ├── vocacional/
│   │   ├── relatorios/
│   │   ├── estoque/
│   │   ├── alimentacao/
│   │   ├── integracoes/
│   │   ├── sync/
│   │   └── notifications/
│   │
│   └── main.py                    # Entrypoint FastAPI — regista todos os routers
│
├── migrations/                    # Alembic (1 BD, schemas separados por módulo)
├── tests/
│   ├── unit/
│   └── integration/
├── Dockerfile
└── pyproject.toml
```



**4.4 Camada de Dados**

|   |   |   |
|---|---|---|
|**Componente**|**Tecnologia**|**Uso**|
|BD única|PostgreSQL 16|Schemas separados por módulo (identity, escolas, directory, etc.)|
|Cache|Redis|Cache de sessões, resultados de queries, rate-limit counters|
|Fila de mensagens|RabbitMQ|Eventos assíncronos para integrações externas e sincronização offline|
|Armazenamento de ficheiros|S3-compatível (Minio/AWS S3)|PDFs, fotos, comprovativos, backups|
|BD Local (offline)|SQLite|Admin local sem conectividade|

**5. Catálogo de Módulos**

**Cada módulo é um pacote Python independente dentro da aplicação, com o seu próprio schema PostgreSQL.**



**5.1 Módulo identity — Identidade e Segurança**

|   |   |
|---|---|
|**Responsabilidade**|SSO (OIDC/OAuth2), gestão de utilizadores, RBAC, licenças por tenant|
|**Endpoints base**|/auth/login, /auth/refresh, /auth/logout, /users, /roles, /tenants, /licenses|
|**Tecnologia**|Python 3.12 + FastAPI + SQLAlchemy 2 + Keycloak SDK|
|**Schema PostgreSQL**|identity|



**5.2 Tabela Completa de Módulos**

|   |   |   |   |
|---|---|---|---|
|**Módulo**|**Domínio**|**Schema PostgreSQL**|**Eventos publicados (event bus interno)**|
|identity|Identidade/Segurança|identity|user.created, user.deactivated, role.changed|
|escolas|Gestão de Escolas|escolas|escola.created, ano_letivo.opened, licenca.suspended|
|directory|Gestão de Pessoas|directory|pessoa.created, aluno.enrolled, professor.assigned|
|enrollment|Matrículas|enrollment|matricula.approved, matricula.rejected, transferencia.completed|
|academico|Académico|academico|turma.created, horario.published, diario.updated|
|avaliacoes|Notas e Faltas|avaliacoes|nota.launched, falta.registered, boletim.generated|
|financeiro|Financeiro|financeiro|fatura.created, pagamento.confirmed, bolsa.granted|
|provas|Concursos/Provas|provas|concurso.opened, prova.applied, ranking.published|
|vocacional|Vocacional|vocacional|questionario.completed, perfil.generated|
|relatorios|Relatórios|relatorios|relatorio.generated, export.completed|
|estoque|Estoque|estoque|item.assigned, stock.low|
|alimentacao|Alimentação|alimentacao|refeicao.registered, subsidio.granted|
|integracoes|Integrações|integracoes|sync.completed, integration.failed|
|sync|Sincronização|sync|delta.sent, delta.received, conflict.detected|
|notifications|Notificações|notifications|notification.sent, notification.failed|

**6. Modelo de Dados — Entidades Centrais por Módulo**

**Todos os módulos partilham a mesma instância PostgreSQL, mas cada um opera exclusivamente no seu schema. As referências entre módulos são feitas por ID (UUID). Queries cross-module são possíveis via JOINs entre schemas quando necessário (vantagem do monólito modular).**



**6.1 Schema: identity**

|   |   |   |
|---|---|---|
|**Tabela**|**Colunas Principais**|**Índices**|
|tenant|id, nome, estado, plano, licenca_validade, configuracao JSONB, created_at|PK: id|
|utilizador|id, tenant_id, pessoa_id, username, senha_hash, tipo, ativo, mfa_segredo, ultimo_login|PK: id; UNIQUE: (tenant_id, username)|
|papel|id, nome, descricao, permissoes JSONB|PK: id|
|utilizador_papel|id, utilizador_id, papel_id, tenant_id, escopo, ativo|UNIQUE: (utilizador_id, papel_id, escopo)|
|sessao|id, utilizador_id, token_hash, ip, user_agent, expira_em|TTL via Redis; PK: id|



**6.2 Schema: escolas**

|   |   |   |
|---|---|---|
|**Tabela**|**Colunas Principais**|**Índices**|
|escola|id, nome, provincia, municipio, commune, endereco, telefone, email, codigo_sige, natureza, nivel_ensino, lat, lng, created_at|PK: id; UNIQUE: codigo_sige|
|ano_letivo|id, escola_id, ano, data_inicio, data_fim, ativo|PK: id; FK: escola_id; UNIQUE: (escola_id, ano) WHERE ativo|
|infraestrutura|id, escola_id, tipo, quantidade, capacidade, estado|PK: id; FK: escola_id|
|configuracao_escola|id, escola_id, chave, valor, updated_at|UNIQUE: (escola_id, chave)|



**6.3 Schema: directory**

|   |   |   |
|---|---|---|
|**Tabela**|**Colunas Principais**|**Índices**|
|pessoa|id, tenant_id, nome_completo, bi_identificacao, dt_nascimento, sexo, nacionalidade, morada, telefone, email, foto_url|PK: id; UNIQUE: (tenant_id, bi_identificacao)|
|aluno|id, tenant_id, pessoa_id, n_processo, ano_ingresso, necessidades_especiais, status|PK: id; UNIQUE: (tenant_id, n_processo)|
|professor|id, tenant_id, pessoa_id, codigo_funcional, especialidade, carga_horaria, tipo_contrato, nivel_academico|PK: id|
|encarregado|id, tenant_id, pessoa_id, profissao, escolaridade|PK: id|
|funcionario|id, tenant_id, pessoa_id, cargo, departamento, data_admissao|PK: id|
|vinculo_aluno_encarregado|id, tenant_id, aluno_id, encarregado_id, tipo, principal|UNIQUE: (aluno_id, encarregado_id)|



**6.4 Schema: enrollment**

|   |   |   |
|---|---|---|
|**Tabela**|**Colunas Principais**|**Índices**|
|matricula|id, tenant_id, aluno_id, ano_letivo_id, classe, turno, estado, data_pedido, data_aprovacao, observacoes|PK: id; UNIQUE: (tenant_id, aluno_id, ano_letivo_id)|
|alocacao_turma|id, matricula_id, turma_id, data_alocacao|PK: id; FK: matricula_id, turma_id|
|transferencia|id, aluno_id, escola_origem_id, escola_destino_id, data_pedido, estado, motivo|PK: id; FK: aluno_id|
|documento_matricula|id, matricula_id, tipo, url, verificado, uploaded_at|PK: id; FK: matricula_id|



**6.5 Convenções de Dados (todos os módulos)**

|   |   |
|---|---|
|**Convenção**|**Regra**|
|Chaves primárias|UUID v4 gerado pelo servidor (nunca auto-increment)|
|tenant_id|Obrigatório e indexado em TODAS as tabelas de dados de negócio|
|Timestamps|created_at e updated_at em TIMESTAMPTZ (sempre UTC) em todas as tabelas|
|Soft delete|deleted_at TIMESTAMPTZ NULL — registos nunca são eliminados fisicamente|
|Auditoria|Tabela audit_log por schema com campos: id, tenant_id, utilizador_id, acao, entidade, entidade_id, dados_antes JSONB, dados_depois JSONB, timestamp, ip|
|Nomes de colunas|snake_case em português (compatibilidade com SIGE/INE)|
|Enums|Definidos como tipos PostgreSQL ENUM para consistência|
|Schemas|Cada módulo opera no seu schema exclusivamente; referências cross-schema por UUID|

**7. Comunicação Entre Módulos**

**7.1 Comunicação Síncrona (In-Process)**

**A principal forma de comunicação entre módulos é via import direto dos serviços de aplicação. Cada módulo expõe uma interface pública (serviços e DTOs) que outros módulos podem consumir.**

```python
# Exemplo: módulo enrollment a consultar o módulo directory
from src.modules.directory.application.services import DirectoryService

class EnrollmentService:
    def __init__(self, directory_service: DirectoryService):
        self.directory = directory_service

    async def create_matricula(self, aluno_id: UUID, ...):
        # Validação cross-module — chamada in-process, sem overhead de rede
        aluno = await self.directory.get_aluno(aluno_id)
        if not aluno:
            raise AlunoNotFoundError(aluno_id)
        ...
```

**Vantagens sobre chamadas REST entre serviços:**

- Sem overhead de rede (latência zero entre módulos);
- Transações ACID cross-module possíveis quando necessário;
- JOINs entre schemas possíveis para relatórios complexos;
- Debugging e tracing simplificados (stack trace único).



**7.2 Comunicação Assíncrona (Event Bus Interno)**

**Para operações que não necessitam de resposta imediata, o sistema usa um event bus in-process que desacopla os módulos:**

|   |   |   |
|---|---|---|
|**Evento**|**Publicador**|**Consumidores**|
|matricula.approved|enrollment|academico, financeiro, notifications|
|nota.launched|avaliacoes|relatorios, notifications|
|pagamento.confirmed|financeiro|notifications, relatorios|
|sync.delta|sync|Módulos relevantes|
|integration.event|integracoes|relatorios, notifications|

**Na fase de evolução para microserviços, o event bus interno será substituído por RabbitMQ para os módulos extraídos, sem alterar a lógica de publicação/consumo.**



**7.3 RabbitMQ (Apenas para Integrações Externas e Sync)**

**Na fase atual, o RabbitMQ é usado apenas para:**

- Sincronização offline (módulo sync ↔ admin local);
- Integrações externas (Multicaixa Express, SIUGEP, INE);
- Jobs assíncronos de longa duração (geração de relatórios pesados).

**7.4 API REST Externa**

**Todos os portais e apps acedem ao backend via API REST:**

|   |   |
|---|---|
|**Padrão**|**Detalhe**|
|Versionamento|/api/v1/... (nunca quebrar sem deprecação de 90 dias)|
|Formato|JSON (request e response)|
|Autenticação|JWT via header Authorization: Bearer {token}|
|Paginação|Cursor-based ou offset/limit (configurável por endpoint)|
|Rate Limiting|Por tenant e por IP via Nginx|

**8. Infraestrutura e Deployment**

**8.1 Topologia de Deployment**

|   |   |   |
|---|---|---|
|**Componente**|**Ambiente Produção (fase inicial)**|**Ambiente Desenvolvimento**|
|Aplicação|Docker container único (FastAPI)|Docker Compose (local)|
|Reverse Proxy|Nginx|Nginx via Docker Compose|
|Base de dados|PostgreSQL gerido (AWS RDS ou equivalente)|PostgreSQL via Docker|
|Cache|Redis gerido ou self-hosted|Redis via Docker|
|Fila (integrações)|RabbitMQ gerido ou self-hosted|RabbitMQ via Docker|
|Ficheiros|S3 (AWS) ou equivalente S3-compatível|MinIO local|
|CDN|CloudFront / Cloudflare|N/A|
|Domínio|siena.gov.ao (domínio oficial)|localhost / .local|



**8.2 Evolução de Infraestrutura**

|   |   |   |
|---|---|---|
|**Fase**|**Infraestrutura**|**Custo estimado**|
|Piloto (1–3 escolas)|1 servidor + 1 PostgreSQL + 1 Redis|$150–300/mês|
|Expansão (50–200 escolas)|2–3 servidores + PostgreSQL com read replicas + Redis Cluster|$500–800/mês|
|Nacional (1.000+ escolas)|Kubernetes + DBs separadas por serviço extraído + RabbitMQ Cluster|$1.500–3.000/mês|



**8.3 Escalabilidade (Fase Inicial)**

- Réplicas horizontais da aplicação FastAPI atrás de Nginx (load balancing);
- Read replicas no PostgreSQL para relatórios e consultas pesadas;
- Redis para cache de sessões e resultados de queries frequentes;
- Jobs assíncronos via background tasks (Celery ou RabbitMQ workers) para relatórios;
- Quotas por tenant para evitar consumo excessivo de recursos por uma escola.



**8.4 Pipeline CI/CD**

|   |   |   |
|---|---|---|
|**Etapa**|**Ferramenta**|**Detalhe**|
|Testes unitários|Pytest + Coverage|Execução em cada push; falha bloqueia merge|
|Testes de integração|Pytest + TestContainers|PostgreSQL real em contentor|
|Análise estática|Ruff + mypy|Linting e type checking obrigatórios|
|Segurança (SAST)|Bandit + Semgrep|Vulnerabilidades comuns no código Python|
|Build da imagem|Docker multi-stage|Imagem final < 150MB, non-root user|
|Deploy staging|GitHub Actions → servidor staging|Automático em merge para develop|
|Deploy produção|GitHub Actions → servidor produção|Manual com aprovação|
|Rollback|Docker rollback ou deploy anterior|Reversão em < 2 minutos|

**9. Estratégia Offline e Sincronização**

**9.1 Admin Local (Modo Offline)**

**O módulo de administração local é uma aplicação desktop instalada na escola. Utiliza SQLite como base de dados local e sincroniza com a nuvem quando a conectividade é restaurada.**

|   |   |   |
|---|---|---|
|**Componente**|**Tecnologia**|**Descrição**|
|App Admin Local|React + Tauri (Rust wrapper)|Interface idêntica ao portal web; funciona 100% offline|
|BD Local|SQLite 3 (WAL mode)|Subconjunto das tabelas de negócio críticas|
|Agente de Sync|Python (serviço Windows/Linux)|Gere sincronização, conflitos e retry|
|Outbox Local|Tabela SQLite change_log|Regista todas as mutações locais|
|Protocolo|HTTPS + HMAC-SHA256 por tenant|Integridade e autenticidade de cada delta|



**9.2 Fluxo de Sincronização**

- 1. Operação local: utilizador executa ação → BD SQLite atualizada + registo em change_log;
- 2. Agente de sync (a cada 5 min ou on demand): lê change_log desde última sync bem-sucedida;
- 3. Delta comprimido (gzip) enviado para o endpoint /api/v1/sync na nuvem com assinatura HMAC;
- 4. Módulo sync valida assinatura, descomprime, aplica delta e devolve delta inverso (nuvem → local);
- 5. Conflitos: LWW por campo com timestamp; entidades críticas (notas aprovadas, matrículas) requerem revisão manual;
- 6. Confirmação: agente regista sync_id e timestamp de última sincronização bem-sucedida;
- 7. Em caso de falha: retry com backoff exponencial; sem perda de dados (outbox persiste).

**10. Decisões Arquitecturais e Trade-offs**

|   |   |   |
|---|---|---|
|**Decisão**|**Alternativa Considerada**|**Justificação da Escolha**|
|Monólito modular primeiro|Microserviços desde o início|Menor custo, menor complexidade operacional, equipa pequena; fronteiras de domínio preservadas; evolução faseada para microserviços quando a escala justificar|
|PostgreSQL único com schemas|BD por serviço (15 instâncias)|Custo 80% menor; JOINs cross-module possíveis para relatórios; migrations centralizadas; isolamento lógico via schemas e RLS|
|Python/FastAPI para o backend|Node.js/Express (stack anterior)|FastAPI oferece tipagem nativa, validação automática (Pydantic), OpenAPI nativo, melhor suporte para análise de dados e IA futura; ecossistema científico robusto para relatórios|
|Event bus interno|RabbitMQ para tudo|Sem overhead de broker na fase inicial; desacoplamento preservado; RabbitMQ introduzido apenas para integrações externas e sync|
|RabbitMQ para integrações|Kafka|Menor complexidade operacional; adequado para o volume inicial; migração para Kafka possível quando o volume justificar|
|Keycloak para SSO|JWT custom implementado|Evita re-implementar um problema crítico de segurança; OIDC/OAuth2 standard; MFA nativo; suporte a federação futura|
|React 18 + Vite|Next.js|Para aplicação de gestão, SPA é suficiente; Vite oferece DX superior e builds mais rápidos; SSR adicionável quando necessário|
|UUID v4 como PKs|Auto-increment inteiros|Seguro para sistemas distribuídos; sem colisões em sync offline; não expõe contadores de registos; compatível com futura extração para microserviços|
|Nginx reverse proxy|Kong API Gateway|Suficiente para a fase inicial; menor complexidade; Kong pode ser adoptado quando houver microserviços a gerir|

**11. Modelo de Segurança Detalhado**

**11.1 Fluxo de Autenticação**

- 1. Utilizador acede ao portal e submete credenciais (username/password + MFA se admin);
- 2. Módulo identity valida credenciais no PostgreSQL (bcrypt comparison);
- 3. Módulo identity emite JWT assinado com RS256 (chave privada em variável de ambiente segura): { sub, tenant_id, papel[], escopo, iat, exp };
- 4. Access token (15 min) + Refresh token (7 dias) devolvidos ao cliente;
- 5. Cliente inclui Authorization: Bearer {access_token} em cada request;
- 6. Middleware FastAPI valida assinatura JWT com chave pública; extrai tenant_id e papel;
- 7. Request processado com contexto de tenant e papel disponível em todo o módulo;
- 8. Módulo aplica autorização por papel/escopo localmente (sem chamada extra);
- 9. Refresh: cliente renova access token com refresh token antes de expirar.



**11.2 RBAC — Papéis e Permissões**

|   |   |   |
|---|---|---|
|**Papel**|**Escopo**|**Permissões Principais**|
|super_admin|Plataforma (todos os tenants)|CRUD em tenants, licenças, configurações globais|
|platform_admin|Plataforma (todos os tenants)|Leitura em todos os tenants; suporte técnico|
|diretor|Escola (tenant_id)|Leitura/escrita em todos os módulos da escola; aprovações|
|secretaria|Escola (tenant_id)|Matrículas, pessoas, financeiro (escrita); sem acesso a salários|
|professor|Turma(s) atribuída(s)|Notas, faltas e diário das suas turmas apenas|
|encarregado|Aluno(s) vinculado(s)|Leitura do boletim, faltas, propinas do seu educando|
|aluno|Próprio perfil|Leitura do próprio boletim, horário, resultados vocacionais|
|gestor_municipal|Município|Leitura de dados consolidados das escolas do município|
|gestor_provincial|Província|Leitura de dados consolidados das escolas da província|
|gestor_nacional|País|Acesso total de leitura; exportações para MED/INE|