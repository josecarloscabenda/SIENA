|                                                                                                                       |
| --------------------------------------------------------------------------------------------------------------------- |
| **SIENA**<br><br>Sistema de Integração Educacional Nacional de Angola<br><br>━━━━━━━━━━━━━━━━━━━━                     |
| **SN 6 — Modelo Relacional**                                                                                          |
| Versão 1.0  \|  Março 2026<br><br>_Modelo de dados completo — 15 schemas, 60+ entidades_                              |

---

## Convenções Globais

Todas as entidades seguem estas regras:

| Regra | Detalhe |
|-------|---------|
| **PK** | `id: UUID v4` (nunca auto-increment) |
| **Multi-tenancy** | `tenant_id: UUID` indexado em todas as tabelas de negócio |
| **Timestamps** | `created_at`, `updated_at` (UTC, preenchidos automaticamente) |
| **Soft Delete** | `deleted_at: DATETIME` nullable — registos nunca são apagados fisicamente |
| **Base Classes** | `BaseModel` (id + timestamps + soft delete), `TenantBaseModel` (+ tenant_id) |
| **Encoding** | UTF-8, JSONB para dados flexíveis |

---

## Mapa de Schemas

```
PostgreSQL: siena
├── identity          ← Autenticação, utilizadores, papéis, tenants
├── escolas           ← Escolas, anos letivos, infraestruturas
├── directory         ← Registo centralizado de pessoas
├── enrollment        ← Matrículas, alocações, transferências
├── academico         ← Currículos, turmas, horários, diário
├── avaliacoes        ← Notas, faltas, boletins
├── financeiro        ← Faturas, pagamentos, bolsas
├── provas            ← Concursos, provas digitais, rankings
├── vocacional        ← Orientação vocacional
├── relatorios        ← Relatórios oficiais, auditoria
├── estoque           ← Inventário (uniformes, livros)
├── alimentacao       ← Refeições, subsídios
├── integracoes       ← Adaptadores para sistemas externos
├── sync              ← Sincronização offline/online
└── notifications     ← Notificações (email, SMS, push)
```

---

## Diagrama de Dependências entre Módulos

```
                    ┌─────────────┐
                    │  identity   │
                    │ (tenant,    │
                    │  utilizador,│
                    │  papel)     │
                    └──────┬──────┘
                           │ tenant_id
              ┌────────────┼────────────────┐
              ▼            ▼                ▼
        ┌──────────┐ ┌──────────┐    ┌────────────┐
        │  escolas  │ │directory │    │ relatorios │
        │ (escola,  │ │(pessoa,  │    │ (auditoria)│
        │  ano_let.)│ │ aluno,   │    └────────────┘
        └────┬─────┘ │ professor│
             │        │ encarreg)│
             │        └────┬─────┘
             │             │
     ┌───────┴──────┐     │
     ▼              ▼     ▼
┌──────────┐  ┌──────────────┐
│enrollment│  │  academico   │
│(matricula│  │(turma,disc., │
│ transf.) │  │ horario,     │
└────┬─────┘  │ diario)      │
     │        └──────┬───────┘
     │               │
     │    ┌──────────┼──────────┐
     ▼    ▼          ▼          ▼
┌──────────┐  ┌──────────┐ ┌──────────┐
│avaliacoes│  │financeiro│ │  provas   │
│(nota,    │  │(fatura,  │ │(concurso,│
│ falta,   │  │ pagam.,  │ │ ranking) │
│ boletim) │  │ bolsa)   │ └──────────┘
└──────────┘  └──────────┘

Módulos auxiliares (ligam a identity + directory):
  vocacional, estoque, alimentacao, integracoes, sync, notifications
```

---

## 01 — identity

### tenant
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| nome | VARCHAR(255) | NOT NULL | Nome da escola/organização |
| estado | VARCHAR(20) | NOT NULL, DEFAULT 'ativo' | ativo, suspensa, expirada |
| plano | VARCHAR(50) | NOT NULL, DEFAULT 'basico' | basico, profissional, enterprise |
| licenca_validade | TIMESTAMPTZ | NULLABLE | Validade da licença |
| configuracao | JSONB | DEFAULT '{}' | Configurações customizadas |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### utilizador
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | FK → identity.tenant, INDEX | |
| pessoa_id | UUID | NULLABLE | FK futuro → directory.pessoa |
| username | VARCHAR(100) | NOT NULL | Único por tenant |
| senha_hash | VARCHAR(255) | NOT NULL | bcrypt (cost ≥ 12) |
| nome_completo | VARCHAR(255) | NOT NULL | |
| email | VARCHAR(255) | NULLABLE | |
| tipo | VARCHAR(30) | DEFAULT 'local' | local, oidc (Keycloak futuro) |
| ativo | BOOLEAN | DEFAULT true | |
| mfa_segredo | VARCHAR(255) | NULLABLE | TOTP secret |
| ultimo_login | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### papel
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| nome | VARCHAR(50) | UNIQUE, NOT NULL | super_admin, diretor, professor, secretaria, aluno, encarregado, gestor_municipal, gestor_provincial, gestor_nacional, platform_admin |
| descricao | TEXT | NULLABLE | |
| permissoes | JSONB | DEFAULT '[]' | Array de permissões |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### utilizador_papel
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| utilizador_id | UUID | FK → identity.utilizador | |
| papel_id | UUID | FK → identity.papel | |
| tenant_id | UUID | FK → identity.tenant, INDEX | |
| escopo | VARCHAR(255) | NULLABLE | escola, turma, municipal, provincial, nacional |
| ativo | BOOLEAN | DEFAULT true | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**UNIQUE:** (utilizador_id, papel_id, escopo)

---

## 02 — escolas

### escola
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | FK → identity.tenant, INDEX | |
| nome | VARCHAR(255) | NOT NULL | |
| codigo_sige | VARCHAR(50) | UNIQUE, NULLABLE | Código SIGE nacional |
| tipo | VARCHAR(50) | DEFAULT 'publica' | publica, privada, comparticipada |
| nivel_ensino | VARCHAR(100) | DEFAULT 'primario' | primario, secundario_1ciclo, secundario_2ciclo, tecnico |
| provincia | VARCHAR(100) | NOT NULL | 18 províncias de Angola |
| municipio | VARCHAR(100) | NOT NULL | |
| comuna | VARCHAR(100) | NULLABLE | |
| endereco | TEXT | NULLABLE | |
| telefone | VARCHAR(30) | NULLABLE | |
| email | VARCHAR(255) | NULLABLE | |
| latitude | FLOAT | NULLABLE | GPS |
| longitude | FLOAT | NULLABLE | GPS |
| ativa | BOOLEAN | DEFAULT true | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### ano_letivo
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | FK → identity.tenant, INDEX | |
| escola_id | UUID | FK → escolas.escola, INDEX | |
| ano | INTEGER | NOT NULL | Ex: 2026 |
| designacao | VARCHAR(50) | NOT NULL | Ex: "2026/2027" |
| data_inicio | DATE | NOT NULL | |
| data_fim | DATE | NOT NULL | |
| ativo | BOOLEAN | DEFAULT false | Apenas 1 ativo por escola |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### infraestrutura
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | FK → identity.tenant, INDEX | |
| escola_id | UUID | FK → escolas.escola, INDEX | |
| nome | VARCHAR(255) | NOT NULL | |
| tipo | VARCHAR(50) | DEFAULT 'sala_aula' | sala_aula, laboratorio, biblioteca, quadra, cantina, administrativo |
| capacidade | INTEGER | NULLABLE | |
| estado | VARCHAR(30) | DEFAULT 'operacional' | operacional, em_reparacao, inoperacional |
| observacoes | TEXT | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### configuracao_escola
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | FK → identity.tenant, INDEX | |
| escola_id | UUID | FK → escolas.escola, UNIQUE | 1:1 com escola |
| num_periodos | INTEGER | DEFAULT 3 | |
| nota_maxima | INTEGER | DEFAULT 20 | |
| nota_minima_aprovacao | INTEGER | DEFAULT 10 | |
| configuracao_extra | JSONB | DEFAULT '{}' | Extensível |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

---

## 03 — directory

### pessoa
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| nome_completo | VARCHAR(255) | NOT NULL | |
| bi_identificacao | VARCHAR(50) | NOT NULL | BI / Cartão de Cidadão |
| dt_nascimento | DATE | NOT NULL | |
| sexo | VARCHAR(1) | NOT NULL | M, F |
| nacionalidade | VARCHAR(100) | DEFAULT 'Angolana' | |
| morada | TEXT | NULLABLE | |
| telefone | VARCHAR(30) | NULLABLE | |
| email | VARCHAR(255) | NULLABLE | |
| foto_url | VARCHAR(500) | NULLABLE | Referência S3 |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**UNIQUE:** (tenant_id, bi_identificacao)

### aluno
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| pessoa_id | UUID | FK → directory.pessoa, INDEX | |
| n_processo | VARCHAR(50) | NOT NULL | Número de processo |
| ano_ingresso | INTEGER | NOT NULL | |
| necessidades_especiais | BOOLEAN | DEFAULT false | |
| status | VARCHAR(20) | DEFAULT 'ativo' | ativo, transferido, desistente, concluinte |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**UNIQUE:** (tenant_id, n_processo)

### professor
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| pessoa_id | UUID | FK → directory.pessoa, INDEX | |
| codigo_funcional | VARCHAR(50) | NOT NULL | |
| especialidade | VARCHAR(100) | NOT NULL | Área de formação |
| carga_horaria_semanal | INTEGER | NOT NULL | |
| tipo_contrato | VARCHAR(20) | DEFAULT 'contrato' | efetivo, contrato, substituto |
| nivel_academico | VARCHAR(100) | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### encarregado
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| pessoa_id | UUID | FK → directory.pessoa, INDEX | |
| profissao | VARCHAR(100) | NULLABLE | |
| escolaridade | VARCHAR(50) | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### funcionario
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| pessoa_id | UUID | FK → directory.pessoa, INDEX | |
| cargo | VARCHAR(100) | NOT NULL | |
| departamento | VARCHAR(100) | NOT NULL | |
| data_admissao | DATE | NOT NULL | |
| tipo_contrato | VARCHAR(20) | DEFAULT 'contrato' | efetivo, contrato |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### vinculo_aluno_encarregado
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| aluno_id | UUID | FK → directory.aluno, INDEX | |
| encarregado_id | UUID | FK → directory.encarregado, INDEX | |
| tipo | VARCHAR(20) | NOT NULL | pai, mae, tutor, outro |
| principal | BOOLEAN | DEFAULT false | Encarregado principal |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**UNIQUE:** (aluno_id, encarregado_id)
**REGRA:** Todo aluno deve ter pelo menos 1 encarregado principal

---

## 04 — enrollment

### matricula
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| aluno_id | UUID | FK → directory.aluno, INDEX | |
| ano_letivo_id | UUID | FK → escolas.ano_letivo, INDEX | |
| classe | VARCHAR(10) | NOT NULL | 1.ª, 7.ª, 10.ª, etc. |
| turno | VARCHAR(20) | DEFAULT 'matutino' | matutino, vespertino, nocturno |
| estado | VARCHAR(20) | DEFAULT 'pendente' | pendente, aprovada, rejeitada, cancelada |
| data_pedido | DATE | NOT NULL | |
| data_aprovacao | DATE | NULLABLE | |
| observacoes | TEXT | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**UNIQUE:** (tenant_id, aluno_id, ano_letivo_id)

### alocacao_turma
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| matricula_id | UUID | FK → enrollment.matricula, INDEX | |
| turma_id | UUID | FK → academico.turma, INDEX | |
| data_alocacao | DATE | NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**REGRA:** Não exceder capacidade_max da turma

### transferencia
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| aluno_id | UUID | FK → directory.aluno, INDEX | |
| escola_origem_id | UUID | FK → escolas.escola | |
| escola_destino_id | UUID | FK → escolas.escola | |
| data_pedido | DATE | NOT NULL | |
| estado | VARCHAR(20) | DEFAULT 'pendente' | pendente, aprovada, rejeitada, cancelada |
| motivo | TEXT | NOT NULL | |
| documentos_url | JSONB | NULLABLE | Array de URLs S3 |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### documento_matricula
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| matricula_id | UUID | FK → enrollment.matricula, INDEX | |
| tipo | VARCHAR(50) | NOT NULL | cartao_cidadao, atestado_vacinacao, foto, etc. |
| url | VARCHAR(500) | NOT NULL | Referência S3 |
| verificado | BOOLEAN | DEFAULT false | |
| uploaded_at | TIMESTAMPTZ | NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

---

## 05 — academico

### curriculo
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| nivel | VARCHAR(50) | NOT NULL | primario, secundario_1ciclo, etc. |
| classe | VARCHAR(10) | NOT NULL | 7.ª, 8.ª, etc. |
| ano_letivo_id | UUID | FK → escolas.ano_letivo, INDEX | |
| carga_horaria_total | INTEGER | NOT NULL | Horas semanais |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### disciplina
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| nome | VARCHAR(255) | NOT NULL | Matemática, Português, etc. |
| codigo | VARCHAR(50) | NOT NULL | Único por tenant |
| curriculo_id | UUID | FK → academico.curriculo, INDEX | |
| carga_horaria_semanal | INTEGER | NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**UNIQUE:** (tenant_id, codigo)

### turma
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| nome | VARCHAR(50) | NOT NULL | 7.ª-A, 10.ª-B, etc. |
| classe | VARCHAR(10) | NOT NULL | |
| turno | VARCHAR(20) | NOT NULL | matutino, vespertino, nocturno |
| ano_letivo_id | UUID | FK → escolas.ano_letivo, INDEX | |
| capacidade_max | INTEGER | NOT NULL | |
| professor_regente_id | UUID | FK → directory.professor, INDEX | |
| sala | VARCHAR(100) | NULLABLE | Sala/infraestrutura |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### horario_aula
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| turma_id | UUID | FK → academico.turma, INDEX | |
| disciplina_id | UUID | FK → academico.disciplina, INDEX | |
| professor_id | UUID | FK → directory.professor, INDEX | |
| dia_semana | VARCHAR(10) | NOT NULL | segunda, terca, quarta, quinta, sexta, sabado |
| hora_inicio | TIME | NOT NULL | |
| hora_fim | TIME | NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**REGRA:** Professor não pode ter 2 aulas simultâneas
**REGRA:** Sala não pode ter 2 turmas simultâneas

### diario_classe
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| turma_id | UUID | FK → academico.turma, INDEX | |
| disciplina_id | UUID | FK → academico.disciplina, INDEX | |
| professor_id | UUID | FK → directory.professor, INDEX | |
| data_aula | DATE | NOT NULL | |
| conteudo | TEXT | NOT NULL | Conteúdo leccionado |
| sumario | TEXT | NOT NULL | Sumário da aula |
| observacoes | TEXT | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### presenca_diario
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| diario_id | UUID | FK → academico.diario_classe, INDEX | |
| aluno_id | UUID | FK → directory.aluno, INDEX | |
| presente | BOOLEAN | NOT NULL | |
| justificativa | TEXT | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

---

## 06 — avaliacoes

### avaliacao
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| turma_id | UUID | FK → academico.turma, INDEX | |
| disciplina_id | UUID | FK → academico.disciplina, INDEX | |
| tipo | VARCHAR(20) | NOT NULL | teste, trabalho, exame, oral |
| periodo | INTEGER | NOT NULL | 1, 2 ou 3 |
| data | DATE | NOT NULL | |
| peso | FLOAT | NOT NULL | Peso na média final |
| nota_maxima | INTEGER | NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### nota
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| avaliacao_id | UUID | FK → avaliacoes.avaliacao, INDEX | |
| aluno_id | UUID | FK → directory.aluno, INDEX | |
| valor | DECIMAL | NOT NULL | ∈ [0, nota_maxima] |
| observacoes | TEXT | NULLABLE | |
| lancado_por | UUID | FK → directory.professor | Professor que lançou |
| lancado_em | TIMESTAMPTZ | NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**REGRA:** Valor deve estar entre 0 e nota_maxima da avaliação
**REGRA:** Editável apenas dentro de janela configurável por escola

### falta
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| aluno_id | UUID | FK → directory.aluno, INDEX | |
| turma_id | UUID | FK → academico.turma, INDEX | |
| disciplina_id | UUID | FK → academico.disciplina, INDEX | |
| data | DATE | NOT NULL | |
| tipo | VARCHAR(20) | NOT NULL | justificada, injustificada |
| justificativa | TEXT | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**REGRA:** Máximo de faltas configurável por escola/nível
**REGRA:** Exceder limite = perda de avaliação (configurável)
**REGRA:** Alerta automático ao encarregado

### regra_media
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| nivel | VARCHAR(50) | NOT NULL | |
| disciplina_id | UUID | FK → academico.disciplina, NULLABLE | NULL = todas |
| formula | VARCHAR(500) | NOT NULL | Fórmula de cálculo |
| minimo_aprovacao | INTEGER | NOT NULL | |
| politica_recuperacao | TEXT | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### boletim
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| aluno_id | UUID | FK → directory.aluno, INDEX | |
| ano_letivo_id | UUID | FK → escolas.ano_letivo, INDEX | |
| periodo | INTEGER | NOT NULL | |
| gerado_em | TIMESTAMPTZ | NOT NULL | |
| url_pdf | VARCHAR(500) | NOT NULL | Referência S3 |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**REGRA:** Só gerado após todas as notas do período inseridas

---

## 07 — financeiro

### plano_pagamento
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| nome | VARCHAR(100) | NOT NULL | |
| periodicidade | VARCHAR(20) | NOT NULL | mensal, trimestral, anual |
| valor_base | DECIMAL | NOT NULL | |
| data_vencimento_dia | INTEGER | NOT NULL | Dia do mês |
| politica_multa | DECIMAL | NULLABLE | % multa |
| politica_juros | DECIMAL | NULLABLE | % juros |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### fatura
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| aluno_id | UUID | FK → directory.aluno, INDEX | |
| plano_id | UUID | FK → financeiro.plano_pagamento | |
| competencia | VARCHAR(10) | NOT NULL | "2026-03" |
| valor_total | DECIMAL | NOT NULL | |
| estado | VARCHAR(20) | DEFAULT 'aberto' | aberto, pago, vencido, estornado |
| vencimento | DATE | NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**REGRA:** Faturas nunca são apagadas, apenas estornadas

### item_fatura
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| fatura_id | UUID | FK → financeiro.fatura, INDEX | |
| descricao | VARCHAR(255) | NOT NULL | Propina, Taxa, etc. |
| quantidade | INTEGER | DEFAULT 1 | |
| valor_unitario | DECIMAL | NOT NULL | |
| desconto | DECIMAL | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### pagamento
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| fatura_id | UUID | FK → financeiro.fatura, INDEX | |
| data | DATE | NOT NULL | |
| valor | DECIMAL | NOT NULL | |
| canal | VARCHAR(30) | NOT NULL | caixa, multicaixa_express, bai_directo, outro |
| nsu_transacao | VARCHAR(50) | NULLABLE | Referência da transacção |
| comprovativo_url | VARCHAR(500) | NULLABLE | S3 |
| registado_por | UUID | FK → identity.utilizador | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**REGRA:** Idempotente por NSU (mesmo NSU nunca processado duas vezes)

### bolsa
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| aluno_id | UUID | FK → directory.aluno, INDEX | |
| tipo | VARCHAR(20) | NOT NULL | percentual, valor |
| valor | DECIMAL | NOT NULL | % ou valor absoluto |
| vigencia_inicio | DATE | NOT NULL | |
| vigencia_fim | DATE | NOT NULL | |
| criterio | TEXT | NULLABLE | |
| aprovado_por | UUID | FK → identity.utilizador | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**REGRA:** Auto-aplicada ao gerar faturas

---

## 08 — provas

### concurso
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| nome | VARCHAR(255) | NOT NULL | |
| organizador | VARCHAR(20) | NOT NULL | ANEP, PIC, outro |
| data_inicio | DATE | NOT NULL | |
| data_fim | DATE | NOT NULL | |
| nivel_minimo | VARCHAR(50) | NOT NULL | |
| nivel_maximo | VARCHAR(50) | NOT NULL | |
| estado | VARCHAR(30) | DEFAULT 'planejamento' | planejamento, aberto, fechado, resultados_publicados |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### inscricao_concurso
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| concurso_id | UUID | FK → provas.concurso, INDEX | |
| aluno_id | UUID | FK → directory.aluno, INDEX | |
| escola_id | UUID | FK → escolas.escola, INDEX | |
| data | DATE | NOT NULL | |
| estado | VARCHAR(20) | DEFAULT 'inscrito' | inscrito, participou, desistiu |
| nota_final | DECIMAL | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**UNIQUE:** (concurso_id, aluno_id)

### prova_digital
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| concurso_id | UUID | FK → provas.concurso, INDEX | |
| turma_id | UUID | FK → academico.turma, NULLABLE | Se prova de sala |
| data_aplicacao | DATE | NOT NULL | |
| duracao_minutos | INTEGER | NOT NULL | |
| estado | VARCHAR(20) | DEFAULT 'nao_iniciada' | nao_iniciada, em_progresso, finalizada |
| chave_antifraude | VARCHAR(100) | NOT NULL | Chave de sessão |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### questao
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| prova_id | UUID | FK → provas.prova_digital, INDEX | |
| enunciado | TEXT | NOT NULL | |
| tipo | VARCHAR(20) | NOT NULL | escolha_multipla, dissertativa, verdadeiro_falso |
| opcoes | JSONB | NULLABLE | Para escolha múltipla |
| resposta_correta | VARCHAR(255) | NULLABLE | Para correcção automática |
| pontuacao | INTEGER | NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### resposta_aluno
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| prova_id | UUID | FK → provas.prova_digital, INDEX | |
| aluno_id | UUID | FK → directory.aluno, INDEX | |
| questao_id | UUID | FK → provas.questao, INDEX | |
| resposta | TEXT | NOT NULL | |
| pontuacao_obtida | INTEGER | NULLABLE | Auto ou manual |
| tempo_resposta | INTEGER | NOT NULL | Segundos |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### ranking_concurso
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| concurso_id | UUID | FK → provas.concurso, INDEX | |
| aluno_id | UUID | FK → directory.aluno, INDEX | |
| escola_id | UUID | FK → escolas.escola, INDEX | |
| posicao_escola | INTEGER | NOT NULL | |
| posicao_municipal | INTEGER | NOT NULL | |
| posicao_nacional | INTEGER | NOT NULL | |
| pontuacao | DECIMAL | NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

---

## 09 — vocacional

### questionario_vocacional
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| nome | VARCHAR(255) | NOT NULL | |
| versao | INTEGER | DEFAULT 1 | |
| questoes | JSONB | NOT NULL | Array de objectos questão |
| ativo | BOOLEAN | DEFAULT true | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### resposta_vocacional
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| questionario_id | UUID | FK → vocacional.questionario_vocacional | |
| aluno_id | UUID | FK → directory.aluno, INDEX | |
| respostas | JSONB | NOT NULL | Respostas por ID de questão |
| completado_em | TIMESTAMPTZ | NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**REGRA:** Disponível apenas para classes 9.ª–12.ª
**REGRA:** Máximo 1 repetição por ano letivo

### perfil_vocacional
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| aluno_id | UUID | FK → directory.aluno, INDEX | |
| areas_interesse | JSONB | NOT NULL | |
| aptidoes | JSONB | NOT NULL | |
| tipo_personalidade | VARCHAR(50) | NOT NULL | |
| completado_em | TIMESTAMPTZ | NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### recomendacao_curso
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| perfil_id | UUID | FK → vocacional.perfil_vocacional | |
| area | VARCHAR(100) | NOT NULL | |
| curso | VARCHAR(255) | NOT NULL | |
| instituicao_sugerida | VARCHAR(255) | NULLABLE | |
| descricao | TEXT | NULLABLE | |
| compatibilidade_pct | INTEGER | NOT NULL | % de compatibilidade |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### relatorio_vocacional
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| aluno_id | UUID | FK → directory.aluno | |
| perfil_id | UUID | FK → vocacional.perfil_vocacional | |
| gerado_em | TIMESTAMPTZ | NOT NULL | |
| url_pdf | VARCHAR(500) | NOT NULL | S3 |
| partilhado_com | JSONB | NULLABLE | IDs com permissão de ver |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

---

## 10 — relatorios

### template_relatorio
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| nome | VARCHAR(255) | NOT NULL | |
| tipo | VARCHAR(20) | NOT NULL | SIGE, INE, MED, interno |
| parametros | JSONB | NOT NULL | Parâmetros configuráveis |
| query_base | TEXT | NOT NULL | Lógica de extracção |
| formato | VARCHAR(10) | NOT NULL | xlsx, pdf, json, csv |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### execucao_relatorio
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| template_id | UUID | FK → relatorios.template_relatorio | |
| solicitado_por | UUID | FK → identity.utilizador | |
| parametros_usados | JSONB | NOT NULL | |
| estado | VARCHAR(20) | DEFAULT 'pendente' | pendente, processando, concluido, erro |
| url_output | VARCHAR(500) | NULLABLE | S3 |
| gerado_em | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### painel
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| nivel | VARCHAR(20) | NOT NULL | escola, municipal, provincial, nacional |
| widgets | JSONB | NOT NULL | Configuração dos widgets |
| configuracao | JSONB | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### registo_auditoria
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| utilizador_id | UUID | FK → identity.utilizador, NULLABLE | |
| acao | VARCHAR(100) | NOT NULL | CREATE, UPDATE, DELETE, EXPORT |
| entidade | VARCHAR(100) | NOT NULL | Tabela afectada |
| entidade_id | UUID | NOT NULL | |
| dados_antes | JSONB | NULLABLE | Snapshot antes |
| dados_depois | JSONB | NULLABLE | Snapshot depois |
| timestamp | TIMESTAMPTZ | NOT NULL | |
| ip | VARCHAR(50) | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**REGRA:** Imutável — nunca editado ou apagado

---

## 11 — estoque

### item_estoque
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| tipo | VARCHAR(30) | NOT NULL | uniforme, livro, material_pedagogico |
| nome | VARCHAR(255) | NOT NULL | |
| descricao | TEXT | NULLABLE | |
| quantidade_total | INTEGER | NOT NULL | |
| quantidade_disponivel | INTEGER | NOT NULL | |
| unidade | VARCHAR(50) | NOT NULL | unidade, caixa, lote |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### atribuicao_item
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| item_id | UUID | FK → estoque.item_estoque, INDEX | |
| aluno_id | UUID | FK → directory.aluno, INDEX | |
| quantidade | INTEGER | NOT NULL | |
| data_atribuicao | DATE | NOT NULL | |
| estado | VARCHAR(20) | DEFAULT 'ativo' | ativo, devolvido, perdido |
| custo | DECIMAL | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### movimento_estoque
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| item_id | UUID | FK → estoque.item_estoque, INDEX | |
| tipo | VARCHAR(20) | NOT NULL | entrada, saida, devolucao, perda |
| quantidade | INTEGER | NOT NULL | |
| data | DATE | NOT NULL | |
| motivo | TEXT | NOT NULL | |
| registado_por | UUID | FK → identity.utilizador | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### alerta_reposicao
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| item_id | UUID | FK → estoque.item_estoque, INDEX | |
| nivel_minimo | INTEGER | NOT NULL | |
| ativo | BOOLEAN | DEFAULT true | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

---

## 12 — alimentacao

### cardapio
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| data | DATE | NOT NULL | |
| turno | VARCHAR(20) | NOT NULL | matutino, vespertino, nocturno |
| descricao | TEXT | NOT NULL | |
| custo_unitario | DECIMAL | NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### consumo_refeicao
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| cardapio_id | UUID | FK → alimentacao.cardapio, INDEX | |
| aluno_id | UUID | FK → directory.aluno, INDEX | |
| presente | BOOLEAN | NOT NULL | |
| subsidiado | BOOLEAN | DEFAULT false | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### subsidio_alimentacao
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| aluno_id | UUID | FK → directory.aluno, INDEX | |
| tipo | VARCHAR(20) | NOT NULL | total, parcial |
| vigencia_inicio | DATE | NOT NULL | |
| vigencia_fim | DATE | NOT NULL | |
| aprovado_por | UUID | FK → identity.utilizador | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### fornecedor
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| nome | VARCHAR(255) | NOT NULL | |
| nif | VARCHAR(20) | NOT NULL | |
| contacto | VARCHAR(255) | NOT NULL | |
| contrato_url | VARCHAR(500) | NULLABLE | S3 |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

---

## 13 — integracoes

### adaptador_integracao
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| nome | VARCHAR(255) | NOT NULL | |
| tipo | VARCHAR(30) | NOT NULL | SIUGEP, INE, GEPE, ANEP, Multicaixa, BAI_Directo |
| endpoint | VARCHAR(500) | NOT NULL | URL da API externa |
| autenticacao | VARCHAR(50) | NOT NULL | apikey, oauth2, hmac |
| estado | VARCHAR(20) | DEFAULT 'ativo' | ativo, inativo, erro |
| ultima_sincronizacao | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**REGRA:** Credenciais guardadas em vault seguro, NÃO na BD

### log_integracao
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| adaptador_id | UUID | FK → integracoes.adaptador_integracao | |
| timestamp | TIMESTAMPTZ | NOT NULL | |
| tipo | VARCHAR(20) | NOT NULL | request, response, erro |
| payload | TEXT | NOT NULL | Sanitizado |
| status_code | INTEGER | NULLABLE | |
| latencia_ms | INTEGER | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### fila_mensagem
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| adaptador_id | UUID | FK → integracoes.adaptador_integracao | |
| payload | JSONB | NOT NULL | |
| estado | VARCHAR(20) | DEFAULT 'pendente' | pendente, processado, erro, DLQ |
| tentativas | INTEGER | DEFAULT 0 | Máx. 5 |
| proximo_retry | TIMESTAMPTZ | NULLABLE | Backoff exponencial |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

---

## 14 — sync

### sessao_sync
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| local_id | VARCHAR(100) | NOT NULL | Identificador do dispositivo |
| ultima_sync_bem_sucedida | TIMESTAMPTZ | NULLABLE | |
| estado | VARCHAR(20) | DEFAULT 'pendente' | sincronizado, pendente, conflito |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### delta_local
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| sessao_sync_id | UUID | FK → sync.sessao_sync | |
| entidade | VARCHAR(100) | NOT NULL | Nome da tabela |
| entidade_id | UUID | NOT NULL | |
| operacao | VARCHAR(10) | NOT NULL | INSERT, UPDATE, DELETE |
| dados | JSONB | NOT NULL | |
| timestamp_local | TIMESTAMPTZ | NOT NULL | |
| sincronizado | BOOLEAN | DEFAULT false | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### conflito_dados
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| entidade | VARCHAR(100) | NOT NULL | |
| entidade_id | UUID | NOT NULL | |
| valor_local | JSONB | NOT NULL | |
| valor_nuvem | JSONB | NOT NULL | |
| resolucao | VARCHAR(20) | NOT NULL | LWW, manual_user, manual_admin |
| resolvido_por | UUID | FK → identity.utilizador, NULLABLE | |
| resolvido_em | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

**REGRA:** LWW (Last-Write-Wins) automático para a maioria das entidades
**REGRA:** Notas e matrículas requerem revisão manual

---

## 15 — notifications

### notificacao
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| tipo | VARCHAR(20) | NOT NULL | email, sms, push_web, in_app |
| destinatario | VARCHAR(255) | NOT NULL | Email ou telefone |
| utilizador_id | UUID | FK → identity.utilizador, NULLABLE | |
| assunto | VARCHAR(255) | NULLABLE | |
| corpo | TEXT | NOT NULL | |
| estado | VARCHAR(20) | DEFAULT 'pendente' | pendente, enviado, falha |
| tentativas | INTEGER | DEFAULT 0 | |
| proxima_tentativa | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### template_notificacao
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| nome | VARCHAR(100) | NOT NULL | falta_alerta, vencimento_fatura, etc. |
| tipo | VARCHAR(20) | NOT NULL | email, sms, push, in_app |
| assunto | VARCHAR(255) | NULLABLE | |
| corpo | TEXT | NOT NULL | Template com {{placeholders}} |
| ativo | BOOLEAN | DEFAULT true | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

### fila_notificacao
| Coluna | Tipo | Constraints | Notas |
|--------|------|-------------|-------|
| id | UUID | PK | |
| tenant_id | UUID | INDEX | |
| notificacao_id | UUID | FK → notifications.notificacao | |
| estado | VARCHAR(20) | DEFAULT 'pendente' | pendente, processado, erro, DLQ |
| tentativas | INTEGER | DEFAULT 0 | |
| proximo_retry | TIMESTAMPTZ | NULLABLE | |
| created_at | TIMESTAMPTZ | NOT NULL | |
| updated_at | TIMESTAMPTZ | NOT NULL | |
| deleted_at | TIMESTAMPTZ | NULLABLE | |

---

## Referências Cruzadas (Foreign Keys entre Módulos)

```
identity.utilizador.pessoa_id ───────────→ directory.pessoa.id (futuro)

escolas.escola.tenant_id ────────────────→ identity.tenant.id
escolas.ano_letivo.escola_id ────────────→ escolas.escola.id

directory.aluno.pessoa_id ───────────────→ directory.pessoa.id
directory.professor.pessoa_id ───────────→ directory.pessoa.id
directory.encarregado.pessoa_id ─────────→ directory.pessoa.id
directory.funcionario.pessoa_id ─────────→ directory.pessoa.id

enrollment.matricula.aluno_id ───────────→ directory.aluno.id
enrollment.matricula.ano_letivo_id ──────→ escolas.ano_letivo.id
enrollment.alocacao_turma.turma_id ──────→ academico.turma.id
enrollment.transferencia.escola_*_id ────→ escolas.escola.id

academico.curriculo.ano_letivo_id ───────→ escolas.ano_letivo.id
academico.turma.ano_letivo_id ───────────→ escolas.ano_letivo.id
academico.turma.professor_regente_id ────→ directory.professor.id
academico.horario_aula.professor_id ─────→ directory.professor.id
academico.presenca_diario.aluno_id ──────→ directory.aluno.id

avaliacoes.avaliacao.turma_id ───────────→ academico.turma.id
avaliacoes.avaliacao.disciplina_id ──────→ academico.disciplina.id
avaliacoes.nota.aluno_id ────────────────→ directory.aluno.id
avaliacoes.nota.lancado_por ─────────────→ directory.professor.id
avaliacoes.falta.aluno_id ───────────────→ directory.aluno.id
avaliacoes.boletim.aluno_id ─────────────→ directory.aluno.id
avaliacoes.boletim.ano_letivo_id ────────→ escolas.ano_letivo.id

financeiro.fatura.aluno_id ──────────────→ directory.aluno.id
financeiro.pagamento.registado_por ──────→ identity.utilizador.id
financeiro.bolsa.aluno_id ───────────────→ directory.aluno.id
financeiro.bolsa.aprovado_por ───────────→ identity.utilizador.id

provas.inscricao_concurso.aluno_id ──────→ directory.aluno.id
provas.inscricao_concurso.escola_id ─────→ escolas.escola.id
provas.prova_digital.turma_id ───────────→ academico.turma.id

vocacional.resposta_vocacional.aluno_id ─→ directory.aluno.id
vocacional.perfil_vocacional.aluno_id ───→ directory.aluno.id

relatorios.execucao_relatorio.solicitado_por → identity.utilizador.id
relatorios.registo_auditoria.utilizador_id ──→ identity.utilizador.id

estoque.atribuicao_item.aluno_id ────────→ directory.aluno.id
estoque.movimento_estoque.registado_por ──→ identity.utilizador.id

alimentacao.consumo_refeicao.aluno_id ───→ directory.aluno.id
alimentacao.subsidio_alimentacao.aluno_id → directory.aluno.id

sync.conflito_dados.resolvido_por ───────→ identity.utilizador.id

notifications.notificacao.utilizador_id ──→ identity.utilizador.id
```

---

## Contadores

| Métrica | Valor |
|---------|-------|
| Schemas | 15 |
| Entidades (tabelas) | 63 |
| Entidades implementadas | 8 (identity: 4, escolas: 4) |
| Foreign keys cross-module | 35+ |
| Módulos com JSONB extensível | 10 |