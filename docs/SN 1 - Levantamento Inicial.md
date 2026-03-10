|                                                                                                                                                      |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **SIENA**<br><br>Sistema de Integração Educacional Nacional de Angola<br><br>━━━━━━━━━━━━━━━━━━━━━━<br><br>_Educar é transformar o futuro de Angola_ |
| **SN 1 — Levantamento Inicial**                                                                                                                      |
| Versão 2.0  \|  Março 2026<br><br>_Confidencial — Para uso interno_                                                                                  |

**1. Objetivo Principal do Sistema**

**O SIENA (Sistema de Integração Educacional Nacional de Angola) é uma plataforma estratégica que visa modernizar e centralizar a gestão da educação em Angola, abrangendo escolas públicas, privadas e público-privadas, do ensino primário ao secundário (ensino médio).**

  

**A plataforma permitirá coletar, armazenar, integrar e analisar informações educacionais referentes a:**

- Escolas e suas infraestruturas;
- Alunos, encarregados de educação e professores;
- Pessoal administrativo e de apoio;
- Matrículas, progressão escolar, notas e resultados;
- Finanças escolares (propinas, bolsas, taxas);
- Relatórios e indicadores de desempenho educacional;
- Concursos e provas nacionais/internacionais;
- Exames vocacionais e orientação profissional.

  

O sistema gerará relatórios oficiais exigidos pelo Ministério da Educação (MED) e pelo Instituto Nacional de Estatística (INE), substituindo processos que ainda dependem do SIGE + Excel. O objetivo final é tornar-se a plataforma nacional de gestão e análise educacional, garantindo maior eficiência, transparência e qualidade no setor.

**2. Identidade Visual**

**A identidade visual do SIENA foi concebida para transmitir confiança, modernidade e compromisso com a educação nacional. Reflete os valores de transparência, rigor e excelência que o sistema quer representar.**

  

**2.1 Nome e Tagline**


|---|---|
|**Nome**|SIENA|
|**Nome completo**|Sistema de Integração Educacional Nacional de Angola|
|**Tagline**|"Educar é transformar o futuro de Angola"|
|**Slogan técnico**|"Dados confiáveis. Decisões melhores. Escolas mais fortes."|

  

**2.2 Paleta de Cores**

**A paleta combina a seriedade institucional com a vitalidade africana:**

  

   
|---|---|---|---|
|■|**Azul Marinho**|#1A3F7A|Confiança, autoridade, educação|
|■|**Verde Esmeralda**|#00A878|Crescimento, progresso, esperança|
|■|**Âmbar / Dourado**|#F5A623|Excelência, destaque, prémio|
|■|**Azul Pálido (fundo)**|#F0F4FA|Fundos de cards, áreas de destaque|

  

**2.3 Tipografia**


|---|---|
|**Fonte principal**|Inter ou Roboto (Google Fonts — open source)|
|**Alternativa corporativa**|Arial / Helvetica Neue|
|**Títulos (peso)**|700 Bold|
|**Subtítulos (peso)**|600 SemiBold|
|**Corpo de texto (peso)**|400 Regular|
|**Notas e legendas**|400 Regular, 87% opacity|

  

**2.4 Logótipo — Conceito**

**O logótipo do SIENA combina o símbolo de um livro aberto com uma seta ascendente integrada, representando o caminho do conhecimento para o futuro. O design deve ser simples, limpo e legível em contextos digitais (web, mobile) e impressos (documentos oficiais, crachás).**

  


|---|---|
|**Símbolo**|Livro aberto com seta ascendente integrada na lombada|
|**Versão principal**|Símbolo + SIENA (texto) em azul marinho|
|**Versão monocromática**|Apenas azul marinho (para documentos oficiais)|
|**Versão invertida**|Branco sobre fundo azul marinho (headers, cabeçalhos)|
|**Espaço mínimo**|20px em torno do logótipo em aplicações digitais|
|**Tamanho mínimo digital**|120px de largura|
|**Tamanho mínimo impresso**|2,5 cm de largura|

  

**2.5 Iconografia e UI**


|---|---|
|**Biblioteca de ícones**|Lucide Icons (open source, consistente)|
|**Estilo**|Line icons, 2px stroke, rounded corners|
|**Grid base**|8px (múltiplos de 8 para espaçamentos e tamanhos)|
|**Bordas arredondadas**|8px para cards, 4px para inputs, 24px para badges|
|**Sombras (elevation)**|Três níveis: leve (4px), médio (8px), forte (16px)|

**3. Utilizadores do Sistema**

**O SIENA serve múltiplas camadas de utilizadores com diferentes necessidades de acesso e funcionalidades:**

  


|---|---|
|**Órgãos Centrais**|Ministério da Educação (MED), GEPE, INADE, INE|
|**Órgãos Locais**|Direções Provinciais, Municipais/Distritais, Coordenações Comunais|
|**Instituições de Ensino**|Escolas públicas, privadas e público-privadas|
|**Parceiros Estratégicos**|ANEP (Associação Nacional do Ensino Particular)|
|**Pessoas (utilizadores diretos)**|Diretores, Professores, Alunos, Encarregados de Educação|
|**Parceiros Internacionais**|UNICEF, UNESCO e outras organizações de apoio ao setor|
|**Equipa Técnica**|Suporte, DevOps, Administração da Plataforma|

**4. Principais Módulos do Sistema**

**O SIENA é estruturado em módulos independentes dentro de um monólito modular com Clean Architecture. Cada módulo corresponde a um domínio de negócio com o seu próprio schema PostgreSQL, garantindo isolamento lógico, manutenção organizada e possibilidade de implantação gradual. A evolução para microserviços será feita de forma faseada, quando o volume e a escala o justificarem.**

  

**4.1 Visão Geral dos Módulos**


|---|
|🏫  **Módulo 01 — Gestão de Escolas**|
|• Cadastro e gestão de escolas (identificação, localização, estatuto legal)|
|• Infraestruturas escolares (salas, laboratórios, bibliotecas, refeitórios)|
|• Gestão de licenças e configurações por instituição|
|• Planos de uso e limites por tenant/escola|


|---|
|👥  **Módulo 02 — Gestão de Pessoas**|
|• Cadastro centralizado de alunos, professores, encarregados e funcionários|
|• Vínculos e relacionamentos entre entidades (aluno–encarregado, professor–disciplina)|
|• Histórico de cargos e funções|


|---|
|📋  **Módulo 03 — Matrículas**|
|• Processo de matrícula presencial e online|
|• Análise, aprovação/rejeição e alocação em turma|
|• Transferências escolares com histórico e rastreabilidade|


|---|
|📚  **Módulo 04 — Académico**|
|• Gestão de turmas, disciplinas e currículo|
|• Horários semanais com gestão de conflitos|
|• Diário de classe digital (conteúdos, sumários, presenças)|


|---|
|📊  **Módulo 05 — Avaliações**|
|• Registo de notas por disciplina, período e tipo de avaliação|
|• Gestão de faltas e impacto em aprovação|
|• Regras de cálculo configuráveis por nível/disciplina|
|• Caderneta escolar digital|



|---|
|💰  **Módulo 06 — Financeiro**|
|• Planos de cobrança por escola (propinas, taxas, matrículas)|
|• Emissão e gestão de faturas, pagamentos e reconciliação|
|• Gestão de bolsas de estudo e apoios sociais|
|• Integração com gateways de pagamento (Multicaixa Express)|


|---|
|🏆  **Módulo 07 — Concursos e Provas**|
|• Plataforma de provas digitais com segurança e antifraude|
|• Gestão de concursos nacionais em parceria com a ANEP|
|• Rankings por aluno, turma, escola e município|
|• Provas Internacionais do Conhecimento (PIC)|


|---|
|🧭  **Módulo 08 — Vocacional**|
|• Questionários de interesses e testes de aptidão para classes 9–12|
|• Relatórios personalizados com perfis vocacionais|
|• Recomendações de cursos/áreas por aluno|
|• Indicadores vocacionais por escola, município e província|


|---|
|📈  **Módulo 09 — Relatórios e Governança**|
|• Relatórios oficiais compatíveis com SIGE/INE e MED|
|• Painéis consolidados por nível administrativo (escola/município/país)|
|• Indicadores: abandono, repetência, sucesso escolar|
|• Auditoria e rastreabilidade de operações|



|---|
|📦  **Módulo 10 — Estoque e Recursos**|
|• Inventário de uniformes (tamanhos, atribuição, reposição)|
|• Inventário de livros (empréstimos, devoluções, perdas)|
|• Alertas de reposição e gestão de lotes|



|---|
|🍽️  **Módulo 11 — Alimentação Escolar**|
|• Planeamento e registo de refeições por aluno/dia|
|• Gestão de subsídios e isenções de alimentação|
|• Controlo de custos e fornecedores|



|---|
|🔗  **Módulo 12 — Integrações**|
|• SIUGEP (certificação de documentos oficiais)|
|• INE e GEPE (exportação estatística)|
|• ANEP (concursos e provas nacionais)|
|• Portais de pagamento (Multicaixa Express, BAI Directo)|
|• Futura compatibilidade com SIGE legado|

  
|                                                             |
| ----------------------------------------------------------- |
| 🔒  **Módulo 13 — Identidade e Segurança**                  |
| • SSO (Single Sign-On) com OIDC/OAuth2                      |
| • RBAC fino por papel e escopo (escola/turma)               |
| • MFA para utilizadores administrativos                     |
| • Conformidade com legislação angolana de proteção de dados |
| • Encriptação em repouso e em trânsito                      |

**5. Abordagem Tecnológica**

**O SIENA adota uma stack moderna, robusta e orientada para escalabilidade nacional. As tecnologias foram selecionadas com base em maturidade, ecossistema, desempenho e adequação ao contexto africano (conectividade variável, equipamentos modestos).**

  

**5.1 Stack Principal**

|                     |                                                                  |
| ------------------- | ---------------------------------------------------------------- |
| **Backend**         | Python (FastAPI) — monólito modular com Clean Architecture       |
| **Frontend Web**    | React 18 + TypeScript (Vite) — SPA com SSR quando necessário     |
| **Mobile**          | React Native — aplicação simplificada para alunos e encarregados |
| **Base de Dados**   | PostgreSQL 16 (primário) + Redis (cache e filas)                 |
| **Mensageria**      | RabbitMQ ou Kafka (comunicação assíncrona entre serviços)        |
| **Autenticação**    | Keycloak (OIDC/OAuth2) ou IdP local compatível                   |
| **Contêineres**     | Docker + Kubernetes (orquestração em produção)                   |
| **API Gateway**     | Kong ou Nginx (roteamento, rate-limit, autenticação)             |
| **Observabilidade** | Prometheus + Grafana + OpenTelemetry (logs JSON)                 |
| **CI/CD**           | GitHub Actions + artefactos versionados com semver               |

  

**5.2 Justificação das Escolhas**


|---|---|
|**Python / FastAPI**|Performance alta (async nativo), tipagem forte, ecossistema científico robusto (pandas, SQLAlchemy), fácil contratação em Angola e Portugal, ideal para relatórios e IA futura|
|**React 18**|Padrão de mercado, ecossistema vasto, curva de aprendizagem acessível, excelente suporte para PWA e modo offline|
|**PostgreSQL**|ACID, multi-tenant com Row-Level Security (RLS), suporte JSON, extensões geoespaciais, maturidade comprovada|
|**Monólito Modular**|Módulos isolados por domínio com schemas separados; deploy simplificado; menor custo de infraestrutura na fase inicial; evolução faseada para microserviços quando a escala justificar|


**5.3 Suporte Offline**

**Dado que muitas escolas angolanas têm conectividade instável, o SIENA implementa uma estratégia offline-first para a camada administrativa local:**

- Módulo administrativo local com base de dados embarcada (SQLite sincronizável);
- Agente de sincronização assíncrono com delta + retries e filas resilientes;
- Política Last-Write-Wins (LWW) com revisão manual para entidades críticas;
- Transporte HTTPS com assinatura HMAC por tenant.

**6. Integrações Previstas**


|                              |                                                              |
| ---------------------------- | ------------------------------------------------------------ |
| **SIUGEP**                   | Certificação e validação de documentos oficiais              |
| **INE / GEPE**               | Exportação de dados estatísticos para o Anuário Educacional  |
| **ANEP**                     | Gestão de concursos, provas nacionais e rankings             |
| **Multicaixa Express / BAI** | Pagamento de propinas, matrículas e taxas online             |
| **MED**                      | Relatórios oficiais exigidos pelo Ministério da Educação     |
| **UNICEF / UNESCO**          | Compatibilidade com indicadores internacionais de educação   |
| **SIGE (legado)**            | Importação de dados históricos (fase de migração controlada) |

**7. Portais de Acesso**

  


|---|---|
|**Portal do Aluno**|Notas, faltas, horário, resultados de concursos, perfil vocacional|
|**Portal do Encarregado**|Desempenho do educando, propinas, comunicados, resultados|
|**Portal do Professor**|Lançamento de notas/faltas, diário de classe, provas online|
|**Portal da Direção**|Gestão global da escola, financeiro, relatórios, estoque|
|**Portal Municipal/Provincial**|Monitoramento regional, rankings, indicadores|
|**Portal Nacional (MED/INE)**|Painéis consolidados, exportações, auditoria nacional|
|**Portal ANEP**|Gestão de concursos, inscrições e rankings nacionais|

**8. Prazos e Entregas**

  

|                |             |                                                                                                           |
| -------------- | ----------- | --------------------------------------------------------------------------------------------------------- |
| **Fase**       | **Prazo**   | **Entregáveis**                                                                                           |
| **Fundação**   | Semanas 1–4 | Infraestrutura, CI/CD, Autenticação (SSO/RBAC), Módulo Escolas, Módulo Pessoas                            |
| **MVP**        | Mês 3       | Matrículas, Turmas, Académico, Notas/Faltas, Portais básicos (Aluno, Professor, Diretor)                  |
| **Versão 1.0** | Mês 6       | Financeiro, Concursos/Provas (ANEP), Vocacional, Relatórios (MED/INE), Integrações externas, Modo offline |
| **Versão 2.0** | Mês 12+     | Estoque, Alimentação escolar, BI ministerial, App mobile completa, Expansão provincial                    |

**9. Equipa de Desenvolvimento**


|---|---|
|**Backend Engineer (x2)**|Python/FastAPI, PostgreSQL, Redis, Docker, arquitetura modular com Clean Architecture|
|**Frontend Engineer (x1)**|React 18 + TypeScript, Vite, PWA, consumo de APIs REST|
|**Mobile Engineer (x1)**|React Native, offline-first, sincronização|
|**DevOps / Infraestrutura (x1)**|Kubernetes, CI/CD, monitorização, segurança|
|**Analista de Negócios / QA (x1)**|Requisitos, testes, documentação, validação com utilizadores|


**Total: 6 perfis (alguns podem ser acumulados na fase inicial). À medida que o projeto escalar para o nível nacional, a equipa deve crescer com engenheiros de dados, especialistas em segurança e gestores de produto.**

**10. Restrições e Pressupostos**

- Conectividade variável nas escolas → estratégia offline-first obrigatória;
- Conformidade com legislação angolana de proteção de dados pessoais;
- Integrações governamentais (SIUGEP, INE) dependem de acordos institucionais formais;
- Treinamento inicial e UX simples para garantir adoção ampla por professores e secretarias;
- O sistema deve suportar o crescimento para todas as províncias de Angola sem redesign arquitectural;
- Dados históricos do SIGE serão importados de forma controlada e validada.