import { useEffect, useState } from "react";
import {
  Building2, Calendar, Eye, MapPin, Phone, Plus, School,
  Search, Settings, X,
} from "lucide-react";
import api from "@/shared/api/client";
import type {
  EscolaResponse,
  EscolaDetailResponse,
  PaginatedResponse,
  CreateEscolaWithTenantRequest,
  CreateEscolaWithTenantResponse,
} from "@/shared/api/types";
import s from "@/shared/styles/common.module.css";
import m from "./EscolasAdmin.module.css";

type CreateTab = "escola" | "pessoa" | "acesso";
type DetailTab = "info" | "config" | "anos";

interface EscolaFields {
  nome: string;
  codigo_sige: string;
  tipo: string;
  nivel_ensino: string;
  provincia: string;
  municipio: string;
  comuna: string;
  endereco: string;
  telefone: string;
  email: string;
}

interface PessoaFields {
  nome_completo: string;
  bi_identificacao: string;
  dt_nascimento: string;
  sexo: string;
  nacionalidade: string;
  morada: string;
  telefone: string;
  email: string;
}

interface AcessoFields {
  username: string;
  password: string;
  password_confirm: string;
}

const EMPTY_ESCOLA: EscolaFields = {
  nome: "", codigo_sige: "", tipo: "publica", nivel_ensino: "primario",
  provincia: "", municipio: "", comuna: "", endereco: "", telefone: "", email: "",
};
const EMPTY_PESSOA: PessoaFields = {
  nome_completo: "", bi_identificacao: "", dt_nascimento: "", sexo: "",
  nacionalidade: "Angolana", morada: "", telefone: "", email: "",
};
const EMPTY_ACESSO: AcessoFields = { username: "", password: "", password_confirm: "" };

const tipoLabel: Record<string, string> = {
  publica: "Publica", privada: "Privada", comparticipada: "Comparticipada",
};
const nivelLabel: Record<string, string> = {
  primario: "Primario", secundario_1ciclo: "Sec. 1. Ciclo",
  secundario_2ciclo: "Sec. 2. Ciclo", tecnico: "Tecnico",
};

export default function EscolasAdmin() {
  const [escolas, setEscolas] = useState<EscolaResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  // Create modal
  const [showCreate, setShowCreate] = useState(false);
  const [createTab, setCreateTab] = useState<CreateTab>("escola");
  const [escola, setEscola] = useState<EscolaFields>({ ...EMPTY_ESCOLA });
  const [pessoa, setPessoa] = useState<PessoaFields>({ ...EMPTY_PESSOA });
  const [acesso, setAcesso] = useState<AcessoFields>({ ...EMPTY_ACESSO });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Detail modal
  const [showDetail, setShowDetail] = useState(false);
  const [detailTab, setDetailTab] = useState<DetailTab>("info");
  const [detail, setDetail] = useState<EscolaDetailResponse | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const fetchEscolas = () => {
    setLoading(true);
    api
      .get<PaginatedResponse<EscolaResponse>>("/escolas/all?limit=100")
      .then(({ data }) => { setEscolas(data.items); setTotal(data.total); })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchEscolas(); }, []);

  // ── Detail modal ─────────────────────────────────
  const openDetail = async (escolaId: string) => {
    setDetailLoading(true);
    setDetail(null);
    setDetailTab("info");
    setShowDetail(true);
    try {
      const { data } = await api.get<EscolaDetailResponse>(`/escolas/all/${escolaId}`);
      setDetail(data);
    } catch {
      setDetail(null);
    } finally {
      setDetailLoading(false);
    }
  };

  // ── Create modal ─────────────────────────────────
  const openCreate = () => {
    setEscola({ ...EMPTY_ESCOLA });
    setPessoa({ ...EMPTY_PESSOA });
    setAcesso({ ...EMPTY_ACESSO });
    setCreateTab("escola");
    setError(""); setSuccess("");
    setShowCreate(true);
  };

  const closeCreate = () => { setShowCreate(false); setError(""); setSuccess(""); };

  const validateTab = (tab: CreateTab): string | null => {
    if (tab === "escola") {
      if (!escola.nome.trim()) return "Nome da escola e obrigatorio.";
      if (!escola.provincia.trim()) return "Provincia e obrigatoria.";
      if (!escola.municipio.trim()) return "Municipio e obrigatorio.";
    }
    if (tab === "pessoa") {
      if (!pessoa.nome_completo.trim()) return "Nome completo e obrigatorio.";
      if (!pessoa.bi_identificacao.trim()) return "BI/Identificacao e obrigatorio.";
      if (!pessoa.dt_nascimento) return "Data de nascimento e obrigatoria.";
      if (!pessoa.sexo) return "Sexo e obrigatorio.";
    }
    if (tab === "acesso") {
      if (!acesso.username.trim()) return "Username e obrigatorio.";
      if (acesso.username.length < 3) return "Username deve ter pelo menos 3 caracteres.";
      if (!acesso.password) return "Password e obrigatoria.";
      if (acesso.password.length < 6) return "Password deve ter pelo menos 6 caracteres.";
      if (acesso.password !== acesso.password_confirm) return "As passwords nao coincidem.";
    }
    return null;
  };

  const goToNextTab = () => {
    const err = validateTab(createTab);
    if (err) { setError(err); return; }
    setError("");
    if (createTab === "escola") setCreateTab("pessoa");
    else if (createTab === "pessoa") setCreateTab("acesso");
  };

  const goToPrevTab = () => {
    setError("");
    if (createTab === "acesso") setCreateTab("pessoa");
    else if (createTab === "pessoa") setCreateTab("escola");
  };

  const handleSubmit = async () => {
    for (const tab of ["escola", "pessoa", "acesso"] as CreateTab[]) {
      const err = validateTab(tab);
      if (err) { setCreateTab(tab); setError(err); return; }
    }
    setError(""); setSaving(true);
    try {
      const payload: CreateEscolaWithTenantRequest = {
        nome: escola.nome, provincia: escola.provincia, municipio: escola.municipio,
        tipo: escola.tipo || "publica", nivel_ensino: escola.nivel_ensino || "primario",
        codigo_sige: escola.codigo_sige || undefined, comuna: escola.comuna || undefined,
        endereco: escola.endereco || undefined, telefone: escola.telefone || undefined,
        email: escola.email || undefined,
        diretor_pessoa: {
          nome_completo: pessoa.nome_completo, bi_identificacao: pessoa.bi_identificacao,
          dt_nascimento: pessoa.dt_nascimento, sexo: pessoa.sexo,
          nacionalidade: pessoa.nacionalidade || "Angolana",
          morada: pessoa.morada || undefined, telefone: pessoa.telefone || undefined,
          email: pessoa.email || undefined,
        },
        diretor_user: { username: acesso.username, password: acesso.password },
      };
      const { data } = await api.post<CreateEscolaWithTenantResponse>("/escolas/with-tenant", payload);
      setSuccess(`Escola "${data.escola.nome}" criada com sucesso! Diretor: ${data.diretor.username}`);
      fetchEscolas();
      setTimeout(() => closeCreate(), 2000);
    } catch (err: unknown) {
      const msg = err && typeof err === "object" && "response" in err
        ? (err as { response: { data: { detail: string } } }).response?.data?.detail
        : "Erro ao criar escola";
      setError(msg || "Erro ao criar escola");
    } finally {
      setSaving(false);
    }
  };

  const filtered = escolas.filter((e) =>
    e.nome.toLowerCase().includes(search.toLowerCase()) ||
    e.provincia.toLowerCase().includes(search.toLowerCase()) ||
    e.municipio.toLowerCase().includes(search.toLowerCase()) ||
    (e.codigo_sige?.toLowerCase().includes(search.toLowerCase()) ?? false),
  );

  const createTabs: { key: CreateTab; label: string; step: number }[] = [
    { key: "escola", label: "Dados da Escola", step: 1 },
    { key: "pessoa", label: "Dados Pessoais do Diretor", step: 2 },
    { key: "acesso", label: "Credenciais de Acesso", step: 3 },
  ];

  const detailTabs: { key: DetailTab; label: string; icon: typeof School }[] = [
    { key: "info", label: "Dados Gerais", icon: Building2 },
    { key: "config", label: "Configuracao", icon: Settings },
    { key: "anos", label: "Anos Letivos", icon: Calendar },
  ];

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>Escolas / Tenants</h1>
          <p className={s.subtitle}>{total} escola(s) na plataforma</p>
        </div>
        <button className={s.btnPrimary} onClick={openCreate}>
          <Plus size={18} /> Nova Escola
        </button>
      </div>

      <div className={s.searchBar}>
        <Search size={18} color="var(--text-muted)" />
        <input
          type="text"
          placeholder="Pesquisar por nome, provincia, municipio ou codigo SIGE..."
          className={s.searchInput}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <p style={{ color: "var(--text-muted)" }}>A carregar...</p>
      ) : filtered.length === 0 ? (
        <p style={{ color: "var(--text-muted)" }}>Nenhuma escola encontrada.</p>
      ) : (
        <div className={s.table}>
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>Tipo</th>
                <th>Nivel</th>
                <th>Provincia</th>
                <th>Municipio</th>
                <th>SIGE</th>
                <th>Estado</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((esc) => (
                <tr key={esc.id} className={m.clickableRow} onClick={() => openDetail(esc.id)}>
                  <td>
                    <span style={{ display: "flex", alignItems: "center", gap: 8, fontWeight: 600 }}>
                      <School size={16} /> {esc.nome}
                    </span>
                  </td>
                  <td>{tipoLabel[esc.tipo] || esc.tipo}</td>
                  <td>{nivelLabel[esc.nivel_ensino] || esc.nivel_ensino}</td>
                  <td>{esc.provincia}</td>
                  <td>{esc.municipio}</td>
                  <td style={{ fontFamily: "monospace", fontSize: "0.8rem" }}>
                    {esc.codigo_sige || "\u2014"}
                  </td>
                  <td>
                    <span className={esc.ativa ? s.badgeSuccess : s.badgeDanger}>
                      {esc.ativa ? "Ativa" : "Inativa"}
                    </span>
                  </td>
                  <td>
                    <Eye size={16} color="var(--text-muted)" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ── Detail Modal ─────────────────────────── */}
      {showDetail && (
        <div className={m.overlay} onClick={() => setShowDetail(false)}>
          <div className={m.modal} onClick={(e) => e.stopPropagation()}>
            <div className={m.modalHeader}>
              <h2>{detail?.nome || "Detalhes da Escola"}</h2>
              <button className={m.closeBtn} onClick={() => setShowDetail(false)}>
                <X size={20} />
              </button>
            </div>

            <div className={m.tabs}>
              {detailTabs.map((t) => (
                <button
                  key={t.key}
                  className={`${m.tab} ${detailTab === t.key ? m.tabActive : ""}`}
                  onClick={() => setDetailTab(t.key)}
                >
                  <t.icon size={16} /> {t.label}
                </button>
              ))}
            </div>

            {detailLoading ? (
              <div className={m.tabContent}>
                <p style={{ color: "var(--text-muted)" }}>A carregar...</p>
              </div>
            ) : detail ? (
              <>
                {detailTab === "info" && (
                  <div className={m.tabContent}>
                    <div className={m.detailGrid}>
                      <div className={m.detailItem}>
                        <span className={m.detailLabel}>Nome</span>
                        <span className={m.detailValue}>{detail.nome}</span>
                      </div>
                      <div className={m.detailItem}>
                        <span className={m.detailLabel}>Codigo SIGE</span>
                        <span className={m.detailValue}>{detail.codigo_sige || "\u2014"}</span>
                      </div>
                      <div className={m.detailItem}>
                        <span className={m.detailLabel}>Tipo</span>
                        <span className={m.detailValue}>{tipoLabel[detail.tipo] || detail.tipo}</span>
                      </div>
                      <div className={m.detailItem}>
                        <span className={m.detailLabel}>Nivel de Ensino</span>
                        <span className={m.detailValue}>{nivelLabel[detail.nivel_ensino] || detail.nivel_ensino}</span>
                      </div>
                      <div className={m.detailItem}>
                        <span className={m.detailLabel}><MapPin size={14} /> Provincia</span>
                        <span className={m.detailValue}>{detail.provincia}</span>
                      </div>
                      <div className={m.detailItem}>
                        <span className={m.detailLabel}>Municipio</span>
                        <span className={m.detailValue}>{detail.municipio}</span>
                      </div>
                      <div className={m.detailItem}>
                        <span className={m.detailLabel}>Comuna</span>
                        <span className={m.detailValue}>{detail.comuna || "\u2014"}</span>
                      </div>
                      <div className={m.detailItem}>
                        <span className={m.detailLabel}>Endereco</span>
                        <span className={m.detailValue}>{detail.endereco || "\u2014"}</span>
                      </div>
                      <div className={m.detailItem}>
                        <span className={m.detailLabel}><Phone size={14} /> Telefone</span>
                        <span className={m.detailValue}>{detail.telefone || "\u2014"}</span>
                      </div>
                      <div className={m.detailItem}>
                        <span className={m.detailLabel}>Email</span>
                        <span className={m.detailValue}>{detail.email || "\u2014"}</span>
                      </div>
                      <div className={m.detailItem}>
                        <span className={m.detailLabel}>Tenant ID</span>
                        <span className={m.detailValue} style={{ fontFamily: "monospace", fontSize: "0.8rem" }}>
                          {detail.tenant_id}
                        </span>
                      </div>
                      <div className={m.detailItem}>
                        <span className={m.detailLabel}>Estado</span>
                        <span className={detail.ativa ? s.badgeSuccess : s.badgeDanger}>
                          {detail.ativa ? "Ativa" : "Inativa"}
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {detailTab === "config" && (
                  <div className={m.tabContent}>
                    {detail.configuracao ? (
                      <div className={m.detailGrid}>
                        <div className={m.detailItem}>
                          <span className={m.detailLabel}>Numero de Periodos</span>
                          <span className={m.detailValue}>{detail.configuracao.num_periodos}</span>
                        </div>
                        <div className={m.detailItem}>
                          <span className={m.detailLabel}>Nota Maxima</span>
                          <span className={m.detailValue}>{detail.configuracao.nota_maxima}</span>
                        </div>
                        <div className={m.detailItem}>
                          <span className={m.detailLabel}>Nota Minima de Aprovacao</span>
                          <span className={m.detailValue}>{detail.configuracao.nota_minima_aprovacao}</span>
                        </div>
                      </div>
                    ) : (
                      <p className={m.emptyMsg}>Sem configuracao definida.</p>
                    )}

                    {detail.infraestruturas.length > 0 && (
                      <>
                        <h3 className={m.sectionTitle}>Infraestruturas</h3>
                        <table className={m.miniTable}>
                          <thead>
                            <tr><th>Nome</th><th>Tipo</th><th>Capacidade</th><th>Estado</th></tr>
                          </thead>
                          <tbody>
                            {detail.infraestruturas.map((inf) => (
                              <tr key={inf.id}>
                                <td>{inf.nome}</td>
                                <td>{inf.tipo}</td>
                                <td>{inf.capacidade ?? "\u2014"}</td>
                                <td>{inf.estado}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </>
                    )}
                  </div>
                )}

                {detailTab === "anos" && (
                  <div className={m.tabContent}>
                    {detail.anos_letivos.length === 0 ? (
                      <p className={m.emptyMsg}>Nenhum ano letivo registado.</p>
                    ) : (
                      <table className={m.miniTable}>
                        <thead>
                          <tr><th>Designacao</th><th>Ano</th><th>Inicio</th><th>Fim</th><th>Estado</th></tr>
                        </thead>
                        <tbody>
                          {detail.anos_letivos.map((al) => (
                            <tr key={al.id}>
                              <td style={{ fontWeight: 600 }}>{al.designacao}</td>
                              <td>{al.ano}</td>
                              <td>{new Date(al.data_inicio).toLocaleDateString("pt-AO")}</td>
                              <td>{new Date(al.data_fim).toLocaleDateString("pt-AO")}</td>
                              <td>
                                <span className={al.ativo ? s.badgeSuccess : s.badgeDanger}>
                                  {al.ativo ? "Ativo" : "Encerrado"}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    )}
                  </div>
                )}
              </>
            ) : (
              <div className={m.tabContent}>
                <p style={{ color: "#e53e3e" }}>Erro ao carregar dados da escola.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Create Modal ─────────────────────────── */}
      {showCreate && (
        <div className={m.overlay} onClick={closeCreate}>
          <div className={m.modal} onClick={(e) => e.stopPropagation()}>
            <div className={m.modalHeader}>
              <h2>Nova Escola / Tenant</h2>
              <button className={m.closeBtn} onClick={closeCreate}><X size={20} /></button>
            </div>

            <div className={m.tabs}>
              {createTabs.map((t) => (
                <button
                  key={t.key}
                  className={`${m.tab} ${createTab === t.key ? m.tabActive : ""}`}
                  onClick={() => { setError(""); setCreateTab(t.key); }}
                >
                  <span className={m.tabStep}>{t.step}</span> {t.label}
                </button>
              ))}
            </div>

            {error && <div className={m.alert} style={{ background: "#FED7D7", color: "#822727" }}>{error}</div>}
            {success && <div className={m.alert} style={{ background: "#C6F6D5", color: "#22543D" }}>{success}</div>}

            {createTab === "escola" && (
              <div className={m.tabContent}>
                <div className={s.formGrid}>
                  <div className={s.formGroup}>
                    <label>Nome da Escola *</label>
                    <input value={escola.nome} onChange={(e) => setEscola({ ...escola, nome: e.target.value })} />
                  </div>
                  <div className={s.formGroup}>
                    <label>Codigo SIGE</label>
                    <input value={escola.codigo_sige} onChange={(e) => setEscola({ ...escola, codigo_sige: e.target.value })} />
                  </div>
                  <div className={s.formGroup}>
                    <label>Tipo</label>
                    <select value={escola.tipo} onChange={(e) => setEscola({ ...escola, tipo: e.target.value })}>
                      <option value="publica">Publica</option>
                      <option value="privada">Privada</option>
                      <option value="comparticipada">Comparticipada</option>
                    </select>
                  </div>
                  <div className={s.formGroup}>
                    <label>Nivel de Ensino</label>
                    <select value={escola.nivel_ensino} onChange={(e) => setEscola({ ...escola, nivel_ensino: e.target.value })}>
                      <option value="primario">Primario</option>
                      <option value="secundario_1ciclo">Sec. 1. Ciclo</option>
                      <option value="secundario_2ciclo">Sec. 2. Ciclo</option>
                      <option value="tecnico">Tecnico</option>
                    </select>
                  </div>
                  <div className={s.formGroup}>
                    <label>Provincia *</label>
                    <input value={escola.provincia} onChange={(e) => setEscola({ ...escola, provincia: e.target.value })} />
                  </div>
                  <div className={s.formGroup}>
                    <label>Municipio *</label>
                    <input value={escola.municipio} onChange={(e) => setEscola({ ...escola, municipio: e.target.value })} />
                  </div>
                  <div className={s.formGroup}>
                    <label>Comuna</label>
                    <input value={escola.comuna} onChange={(e) => setEscola({ ...escola, comuna: e.target.value })} />
                  </div>
                  <div className={s.formGroup}>
                    <label>Endereco</label>
                    <input value={escola.endereco} onChange={(e) => setEscola({ ...escola, endereco: e.target.value })} />
                  </div>
                  <div className={s.formGroup}>
                    <label>Telefone</label>
                    <input value={escola.telefone} onChange={(e) => setEscola({ ...escola, telefone: e.target.value })} />
                  </div>
                  <div className={s.formGroup}>
                    <label>Email</label>
                    <input type="email" value={escola.email} onChange={(e) => setEscola({ ...escola, email: e.target.value })} />
                  </div>
                </div>
              </div>
            )}

            {createTab === "pessoa" && (
              <div className={m.tabContent}>
                <div className={s.formGrid}>
                  <div className={s.formGroup}>
                    <label>Nome Completo *</label>
                    <input value={pessoa.nome_completo} onChange={(e) => setPessoa({ ...pessoa, nome_completo: e.target.value })} />
                  </div>
                  <div className={s.formGroup}>
                    <label>BI / Identificacao *</label>
                    <input value={pessoa.bi_identificacao} onChange={(e) => setPessoa({ ...pessoa, bi_identificacao: e.target.value })} />
                  </div>
                  <div className={s.formGroup}>
                    <label>Data de Nascimento *</label>
                    <input type="date" value={pessoa.dt_nascimento} onChange={(e) => setPessoa({ ...pessoa, dt_nascimento: e.target.value })} />
                  </div>
                  <div className={s.formGroup}>
                    <label>Sexo *</label>
                    <select value={pessoa.sexo} onChange={(e) => setPessoa({ ...pessoa, sexo: e.target.value })}>
                      <option value="">Selecionar...</option>
                      <option value="M">Masculino</option>
                      <option value="F">Feminino</option>
                    </select>
                  </div>
                  <div className={s.formGroup}>
                    <label>Nacionalidade</label>
                    <input value={pessoa.nacionalidade} onChange={(e) => setPessoa({ ...pessoa, nacionalidade: e.target.value })} />
                  </div>
                  <div className={s.formGroup}>
                    <label>Morada</label>
                    <input value={pessoa.morada} onChange={(e) => setPessoa({ ...pessoa, morada: e.target.value })} />
                  </div>
                  <div className={s.formGroup}>
                    <label>Telefone</label>
                    <input value={pessoa.telefone} onChange={(e) => setPessoa({ ...pessoa, telefone: e.target.value })} />
                  </div>
                  <div className={s.formGroup}>
                    <label>Email</label>
                    <input type="email" value={pessoa.email} onChange={(e) => setPessoa({ ...pessoa, email: e.target.value })} />
                  </div>
                </div>
              </div>
            )}

            {createTab === "acesso" && (
              <div className={m.tabContent}>
                <p className={m.tabDesc}>Credenciais que o diretor utilizara para aceder ao portal de gestao.</p>
                <div className={s.formGrid}>
                  <div className={s.formGroup}>
                    <label>Username *</label>
                    <input value={acesso.username} onChange={(e) => setAcesso({ ...acesso, username: e.target.value })} />
                  </div>
                  <div className={s.formGroup} />
                  <div className={s.formGroup}>
                    <label>Password *</label>
                    <input type="password" value={acesso.password} onChange={(e) => setAcesso({ ...acesso, password: e.target.value })} />
                  </div>
                  <div className={s.formGroup}>
                    <label>Confirmar Password *</label>
                    <input type="password" value={acesso.password_confirm} onChange={(e) => setAcesso({ ...acesso, password_confirm: e.target.value })} />
                  </div>
                </div>
              </div>
            )}

            <div className={m.modalFooter}>
              {createTab !== "escola" && (
                <button className={s.btnSecondary} onClick={goToPrevTab}>Anterior</button>
              )}
              <div style={{ flex: 1 }} />
              {createTab !== "acesso" ? (
                <button className={s.btnPrimary} onClick={goToNextTab}>Proximo</button>
              ) : (
                <button className={s.btnPrimary} onClick={handleSubmit} disabled={saving}>
                  {saving ? "A criar..." : "Criar Escola e Tenant"}
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
