export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface TenantPublicResponse {
  id: string;
  nome: string;
  slug: string;
}

export interface UserResponse {
  id: string;
  tenant_id: string;
  username: string;
  nome_completo: string;
  email: string | null;
  ativo: boolean;
  papeis: string[];
  ultimo_login: string | null;
  created_at: string;
  // Identidades derivadas (NULL se utilizador não tem o papel)
  pessoa_id: string | null;
  professor_id: string | null;
  aluno_id: string | null;
  encarregado_id: string | null;
}

export interface EscolaResponse {
  id: string;
  tenant_id: string;
  nome: string;
  codigo_sige: string | null;
  tipo: string;
  nivel_ensino: string;
  provincia: string;
  municipio: string;
  comuna: string | null;
  endereco: string | null;
  telefone: string | null;
  email: string | null;
  latitude: number | null;
  longitude: number | null;
  ativa: boolean;
  created_at: string;
}

export interface EscolaDetailResponse extends EscolaResponse {
  anos_letivos: AnoLetivoResponse[];
  infraestruturas: InfraestruturaResponse[];
  configuracao: ConfiguracaoEscolaResponse | null;
}

export interface AnoLetivoResponse {
  id: string;
  escola_id: string;
  ano: number;
  designacao: string;
  data_inicio: string;
  data_fim: string;
  ativo: boolean;
  created_at: string;
}

export interface InfraestruturaResponse {
  id: string;
  escola_id: string;
  nome: string;
  tipo: string;
  capacidade: number | null;
  estado: string;
  observacoes: string | null;
  created_at: string;
}

export interface ConfiguracaoEscolaResponse {
  id: string;
  escola_id: string;
  num_periodos: number;
  nota_maxima: number;
  nota_minima_aprovacao: number;
  configuracao_extra: Record<string, unknown> | null;
}

// ── Admin: Criar Escola com Tenant ───────────

export interface DiretorPessoaData {
  nome_completo: string;
  bi_identificacao: string;
  dt_nascimento: string;
  sexo: string;
  nacionalidade?: string;
  morada?: string;
  telefone?: string;
  email?: string;
}

export interface DiretorUserData {
  username: string;
  password: string;
}

export interface CreateEscolaWithTenantRequest {
  nome: string;
  provincia: string;
  municipio: string;
  tipo?: string;
  nivel_ensino?: string;
  codigo_sige?: string;
  comuna?: string;
  endereco?: string;
  telefone?: string;
  email?: string;
  diretor_pessoa: DiretorPessoaData;
  diretor_user: DiretorUserData;
}

export interface DiretorResponse {
  id: string;
  username: string;
  nome_completo: string;
  email: string | null;
}

export interface PessoaSimpleResponse {
  id: string;
  nome_completo: string;
  bi_identificacao: string;
  sexo: string;
}

export interface CreateEscolaWithTenantResponse {
  tenant_id: string;
  escola: EscolaResponse;
  diretor: DiretorResponse;
  pessoa: PessoaSimpleResponse;
}

export interface PaginatedResponse<T> {
  total: number;
  offset: number;
  limit: number;
  items: T[];
}

export interface PapelResponse {
  id: string;
  nome: string;
  descricao: string | null;
}

// ── Directory ─────────────────────────────────

export interface PessoaResponse {
  id: string;
  tenant_id: string;
  nome_completo: string;
  bi_identificacao: string;
  dt_nascimento: string;
  sexo: string;
  nacionalidade: string;
  morada: string | null;
  telefone: string | null;
  email: string | null;
  foto_url: string | null;
  created_at: string;
}

export interface AlunoResponse {
  id: string;
  tenant_id: string;
  pessoa_id: string;
  n_processo: string;
  ano_ingresso: number;
  necessidades_especiais: boolean;
  status: string;
  created_at: string;
  pessoa: PessoaResponse;
}

export interface AlunoDetailResponse extends AlunoResponse {
  vinculos: VinculoResponse[];
}

export interface ProfessorResponse {
  id: string;
  tenant_id: string;
  pessoa_id: string;
  codigo_funcional: string;
  especialidade: string;
  carga_horaria_semanal: number;
  tipo_contrato: string;
  nivel_academico: string | null;
  created_at: string;
  pessoa: PessoaResponse;
}

export interface EncarregadoResponse {
  id: string;
  tenant_id: string;
  pessoa_id: string;
  profissao: string | null;
  escolaridade: string | null;
  created_at: string;
  pessoa: PessoaResponse;
}

export interface VinculoResponse {
  id: string;
  aluno_id: string;
  encarregado_id: string;
  tipo: string;
  principal: boolean;
  created_at: string;
  encarregado: EncarregadoResponse | null;
}

// ── Enrollment ────────────────────────────────

export interface MatriculaResponse {
  id: string;
  tenant_id: string;
  aluno_id: string;
  aluno_nome: string | null;
  aluno_n_processo: string | null;
  ano_letivo_id: string;
  ano_letivo_designacao: string | null;
  classe: string;
  turno: string;
  estado: string;
  data_pedido: string;
  data_aprovacao: string | null;
  observacoes: string | null;
  created_at: string;
}

export interface MatriculaDetailResponse extends MatriculaResponse {
  alocacao: AlocacaoTurmaResponse | null;
  documentos: DocumentoMatriculaResponse[];
}

export interface AlocacaoTurmaResponse {
  id: string;
  matricula_id: string;
  turma_id: string;
  data_alocacao: string;
  created_at: string;
}

export interface TransferenciaResponse {
  id: string;
  tenant_id: string;
  aluno_id: string;
  escola_origem_id: string;
  escola_destino_id: string;
  data_pedido: string;
  estado: string;
  motivo: string;
  documentos_url: Record<string, unknown> | null;
  created_at: string;
}

export interface DocumentoMatriculaResponse {
  id: string;
  matricula_id: string;
  tipo: string;
  url: string;
  verificado: boolean;
  uploaded_at: string;
  created_at: string;
}

// ── Académico ─────────────────────────────────

export interface CurriculoResponse {
  id: string;
  tenant_id: string;
  nivel: string;
  classe: string;
  ano_letivo_id: string;
  ano_letivo_designacao: string | null;
  carga_horaria_total: number;
  created_at: string;
}

export interface CurriculoDetailResponse extends CurriculoResponse {
  disciplinas: DisciplinaResponse[];
}

export interface DisciplinaResponse {
  id: string;
  tenant_id: string;
  nome: string;
  codigo: string;
  curriculo_id: string;
  curriculo_nome: string | null;
  carga_horaria_semanal: number;
  created_at: string;
}

export interface TurmaResponse {
  id: string;
  tenant_id: string;
  nome: string;
  classe: string;
  turno: string;
  ano_letivo_id: string;
  ano_letivo_designacao: string | null;
  capacidade_max: number;
  professor_regente_id: string;
  professor_regente_nome: string | null;
  sala: string | null;
  created_at: string;
}

export interface TurmaDetailResponse extends TurmaResponse {
  horarios: HorarioAulaResponse[];
}

export interface HorarioAulaResponse {
  id: string;
  turma_id: string;
  disciplina_id: string;
  disciplina_nome: string | null;
  professor_id: string;
  professor_nome: string | null;
  dia_semana: string;
  hora_inicio: string;
  hora_fim: string;
  created_at: string;
}

export interface DiarioClasseResponse {
  id: string;
  tenant_id: string;
  turma_id: string;
  disciplina_id: string;
  professor_id: string;
  data_aula: string;
  conteudo: string;
  sumario: string;
  observacoes: string | null;
  created_at: string;
  presencas: PresencaResponse[];
}

export interface PresencaResponse {
  id: string;
  diario_id: string;
  aluno_id: string;
  presente: boolean;
  justificativa: string | null;
}

// ── Avaliações ────────────────────────────────

export interface AvaliacaoResponse {
  id: string;
  tenant_id: string;
  turma_id: string;
  turma_nome: string | null;
  disciplina_id: string;
  disciplina_nome: string | null;
  tipo: string;
  periodo: number;
  data: string;
  peso: number;
  nota_maxima: number;
  created_at: string;
}

export interface NotaResponse {
  id: string;
  avaliacao_id: string;
  aluno_id: string;
  aluno_nome: string | null;
  aluno_n_processo: string | null;
  valor: number;
  observacoes: string | null;
  lancado_por: string;
  lancado_em: string;
  created_at: string;
}

export interface FaltaResponse {
  id: string;
  aluno_id: string;
  aluno_nome: string | null;
  turma_id: string;
  turma_nome: string | null;
  disciplina_id: string;
  disciplina_nome: string | null;
  data: string;
  tipo: string;
  justificativa: string | null;
  created_at: string;
}

// ── Lookup DTOs (dropdowns) ───────────────────

export interface AlunoLookupItem {
  id: string;
  nome: string;
  n_processo: string;
}

export interface ProfessorLookupItem {
  id: string;
  nome: string;
  codigo_funcional: string;
  especialidade: string;
}

export interface EncarregadoLookupItem {
  id: string;
  nome: string;
  bi_identificacao: string;
  telefone: string | null;
}

export interface DisciplinaLookupItem {
  id: string;
  nome: string;
  codigo: string;
  curriculo_id: string;
}

export interface TurmaLookupItem {
  id: string;
  nome: string;
  classe: string;
  turno: string;
  ano_letivo_id: string;
}

export interface CurriculoLookupItem {
  id: string;
  nome: string;
  nivel: string;
  classe: string;
}

export interface AnoLetivoLookupItem {
  id: string;
  designacao: string;
  ano: number;
  ativo: boolean;
  escola_id: string;
}

export interface EscolaLookupItem {
  id: string;
  nome: string;
  provincia: string;
  municipio: string;
}

// ── Sprint 2 backend (Dev A) — relação por turma/professor/aluno ────────

export interface TurmaAlunoItem {
  aluno_id: string;
  matricula_id: string;
  alocacao_id: string;
  nome: string;
  n_processo: string;
  data_alocacao: string;
}

export interface ProfessorTurmaItem {
  turma_id: string;
  nome: string;
  classe: string;
  turno: string;
  ano_letivo_id: string;
  ano_letivo_designacao: string;
  is_regente: boolean;
  leciona_disciplinas: number;
}

export interface ProfessorDisciplinaItem {
  disciplina_id: string;
  nome: string;
  codigo: string;
  curriculo_id: string;
  turmas_count: number;
}

export interface AlunoEncarregadoItem {
  encarregado_id: string;
  pessoa_id: string;
  nome: string;
  bi_identificacao: string;
  telefone: string | null;
  email: string | null;
  profissao: string | null;
  tipo: string;
  principal: boolean;
}

// ── Sprint 3: Dashboards ─────────────────────────

export interface GestaoStats {
  total_alunos: number;
  total_alunos_ativos: number;
  total_professores: number;
  total_encarregados: number;
  total_turmas: number;
  total_disciplinas: number;
  matriculas_pendentes: number;
  matriculas_aprovadas: number;
  matriculas_rejeitadas: number;
  avaliacoes_total: number;
  notas_lancadas: number;
  faltas_periodo_atual: number;
}

export interface ProximaAulaItem {
  horario_id: string;
  turma_id: string;
  turma_nome: string;
  disciplina_id: string;
  disciplina_nome: string;
  dia_semana: string;
  hora_inicio: string;
  hora_fim: string;
}

export interface TurmaResumoProfessor {
  turma_id: string;
  nome: string;
  classe: string;
  turno: string;
  is_regente: boolean;
  leciona_disciplinas: number;
  total_alunos: number;
}

export interface ProfessorStats {
  professor_id: string;
  nome: string;
  turmas_atribuidas: number;
  disciplinas_lecciona: number;
  total_alunos: number;
  notas_por_lancar: number;
  proximas_aulas: ProximaAulaItem[];
  turmas: TurmaResumoProfessor[];
}

export interface AlunoDisciplinaResumo {
  disciplina_id: string;
  disciplina_nome: string;
  media: string | null;
  faltas: number;
}

export interface ProximaAvaliacaoItem {
  avaliacao_id: string;
  disciplina_id: string;
  disciplina_nome: string;
  tipo: string;
  data: string;
  nota_maxima: number;
}

export interface AlunoStats {
  aluno_id: string;
  nome: string;
  n_processo: string;
  matricula_id: string | null;
  classe: string | null;
  turma_id: string | null;
  turma_nome: string | null;
  media_geral: string | null;
  total_faltas: number;
  faltas_justificadas: number;
  faltas_injustificadas: number;
  proximas_avaliacoes: ProximaAvaliacaoItem[];
  disciplinas: AlunoDisciplinaResumo[];
}

export interface EducandoResumo {
  aluno_id: string;
  nome: string;
  n_processo: string;
  classe: string | null;
  turma_nome: string | null;
  media_geral: string | null;
  total_faltas: number;
  faltas_injustificadas: number;
}

export interface EncarregadoStats {
  encarregado_id: string;
  nome: string;
  educandos: EducandoResumo[];
}

export interface PautaAlunoLinha {
  aluno_id: string;
  matricula_id: string;
  nome: string;
  n_processo: string;
  medias_por_disciplina: Record<string, string | null>;
  media_geral: string | null;
}

export interface PautaResponse {
  turma_id: string;
  turma_nome: string;
  classe: string;
  ano_letivo_designacao: string | null;
  periodo: number;
  disciplinas: { id: string; nome: string; codigo: string }[];
  linhas: PautaAlunoLinha[];
}

export interface FaltaResumoResponse {
  total: number;
  justificadas: number;
  injustificadas: number;
  por_disciplina: { disciplina_id: string; total: number }[];
}

export interface BoletimDisciplinaItem {
  disciplina_id: string;
  disciplina_nome: string;
  media: number | null;
  faltas_total: number;
}

export interface BoletimResponse {
  aluno_id: string;
  ano_letivo_id: string;
  periodo: number;
  disciplinas: BoletimDisciplinaItem[];
}