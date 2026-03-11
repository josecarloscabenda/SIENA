export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
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