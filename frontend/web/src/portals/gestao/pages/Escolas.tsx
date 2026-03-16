import { useEffect, useState } from "react";
import {
  Building2, Edit2, MapPin, Phone, Mail, Plus, Trash2,
} from "lucide-react";
import api from "@/shared/api/client";
import type {
  EscolaDetailResponse,
  InfraestruturaResponse,
} from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

type Tab = "info" | "infra" | "anos" | "config";

const tipoLabel: Record<string, string> = {
  publica: "Pública",
  privada: "Privada",
  comparticipada: "Comparticipada",
};
const nivelLabel: Record<string, string> = {
  primario: "Primário",
  secundario_1ciclo: "Sec. 1.º Ciclo",
  secundario_2ciclo: "Sec. 2.º Ciclo",
  tecnico: "Técnico",
};
const infraTipoLabel: Record<string, string> = {
  sala_aula: "Sala de Aula",
  laboratorio: "Laboratório",
  biblioteca: "Biblioteca",
  quadra: "Quadra",
  cantina: "Cantina",
  administrativo: "Administrativo",
};
const estadoInfraLabel: Record<string, string> = {
  operacional: "Operacional",
  em_reparacao: "Em Reparação",
  inoperacional: "Inoperacional",
};
const estadoInfraBadge: Record<string, string> = {
  operacional: s.badgeGreen,
  em_reparacao: s.badgeYellow,
  inoperacional: s.badgeRed,
};

interface InfraForm {
  nome: string;
  tipo: string;
  capacidade: string;
  estado: string;
  observacoes: string;
}
const emptyInfraForm: InfraForm = {
  nome: "",
  tipo: "sala_aula",
  capacidade: "",
  estado: "operacional",
  observacoes: "",
};

export default function Escolas() {
  const { hasRole } = useAuth();
  const [escola, setEscola] = useState<EscolaDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<Tab>("info");
  const [error, setError] = useState("");

  /* Infra state */
  const [infras, setInfras] = useState<InfraestruturaResponse[]>([]);
  const [showInfraForm, setShowInfraForm] = useState(false);
  const [editingInfraId, setEditingInfraId] = useState<string | null>(null);
  const [infraForm, setInfraForm] = useState<InfraForm>(emptyInfraForm);
  const [infraSaving, setInfraSaving] = useState(false);

  const canManage = hasRole("super_admin", "diretor", "secretaria");

  const fetchEscola = () => {
    setLoading(true);
    api
      .get<{ items: EscolaDetailResponse[] }>("/escolas?limit=1")
      .then(({ data }) => {
        if (data.items.length > 0) {
          const e = data.items[0];
          return api.get<EscolaDetailResponse>(`/escolas/${e.id}`);
        }
        return null;
      })
      .then((res) => {
        if (res) {
          setEscola(res.data);
          setInfras(res.data.infraestruturas || []);
        }
      })
      .catch(() => setError("Erro ao carregar dados da escola"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchEscola();
  }, []);

  const refreshInfras = () => {
    if (!escola) return;
    api
      .get<InfraestruturaResponse[]>(`/escolas/${escola.id}/infraestruturas`)
      .then(({ data }) => setInfras(data))
      .catch(() => {});
  };

  const openAddInfra = () => {
    setInfraForm(emptyInfraForm);
    setEditingInfraId(null);
    setShowInfraForm(true);
    setError("");
  };

  const openEditInfra = (infra: InfraestruturaResponse) => {
    setInfraForm({
      nome: infra.nome,
      tipo: infra.tipo,
      capacidade: infra.capacidade?.toString() || "",
      estado: infra.estado,
      observacoes: infra.observacoes || "",
    });
    setEditingInfraId(infra.id);
    setShowInfraForm(true);
    setError("");
  };

  const handleSaveInfra = async () => {
    if (!escola) return;
    setInfraSaving(true);
    setError("");
    const payload = {
      nome: infraForm.nome,
      tipo: infraForm.tipo,
      capacidade: infraForm.capacidade ? parseInt(infraForm.capacidade) : null,
      estado: infraForm.estado,
      observacoes: infraForm.observacoes || null,
    };
    try {
      if (editingInfraId) {
        await api.patch(`/escolas/${escola.id}/infraestruturas/${editingInfraId}`, payload);
      } else {
        await api.post(`/escolas/${escola.id}/infraestruturas`, payload);
      }
      setShowInfraForm(false);
      refreshInfras();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao guardar infraestrutura");
    } finally {
      setInfraSaving(false);
    }
  };

  const handleDeleteInfra = async (id: string) => {
    if (!escola || !confirm("Tem certeza que deseja eliminar esta infraestrutura?")) return;
    try {
      await api.delete(`/escolas/${escola.id}/infraestruturas/${id}`);
      refreshInfras();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Erro ao eliminar");
    }
  };

  if (loading) return <p className={s.muted}>A carregar...</p>;
  if (!escola) return <p className={s.muted}>Nenhuma escola encontrada para este tenant.</p>;

  const tabs: { key: Tab; label: string }[] = [
    { key: "info", label: "Dados Gerais" },
    { key: "infra", label: `Infraestrutura (${infras.length})` },
    { key: "anos", label: `Anos Letivos (${escola.anos_letivos?.length || 0})` },
    { key: "config", label: "Configuração" },
  ];

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>
            <span style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <Building2 size={24} />
              {escola.nome}
            </span>
          </h1>
          <p className={s.subtitle}>
            {tipoLabel[escola.tipo] || escola.tipo} — {nivelLabel[escola.nivel_ensino] || escola.nivel_ensino}
          </p>
        </div>
      </div>

      {error && <div className={s.error}>{error}</div>}

      <div className={s.tabs}>
        {tabs.map((t) => (
          <button
            key={t.key}
            className={`${s.tab} ${tab === t.key ? s.tabActive : ""}`}
            onClick={() => setTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab: Info */}
      {tab === "info" && (
        <div className={s.form}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
            <InfoItem label="Nome" value={escola.nome} />
            <InfoItem label="Código SIGE" value={escola.codigo_sige || "—"} />
            <InfoItem label="Tipo" value={tipoLabel[escola.tipo] || escola.tipo} />
            <InfoItem label="Nível de Ensino" value={nivelLabel[escola.nivel_ensino] || escola.nivel_ensino} />
            <InfoItem label="Província" value={escola.provincia} icon={<MapPin size={14} />} />
            <InfoItem label="Município" value={escola.municipio} />
            <InfoItem label="Comuna" value={escola.comuna || "—"} />
            <InfoItem label="Endereço" value={escola.endereco || "—"} />
            <InfoItem label="Telefone" value={escola.telefone || "—"} icon={<Phone size={14} />} />
            <InfoItem label="Email" value={escola.email || "—"} icon={<Mail size={14} />} />
            <InfoItem label="Estado" value={escola.ativa ? "Ativa" : "Inativa"} />
            <InfoItem label="Criada em" value={new Date(escola.created_at).toLocaleDateString("pt-AO")} />
          </div>
        </div>
      )}

      {/* Tab: Infraestrutura */}
      {tab === "infra" && (
        <div>
          {canManage && (
            <div style={{ marginBottom: 16 }}>
              <button className={s.addBtn} onClick={openAddInfra}>
                <Plus size={18} />
                Adicionar Infraestrutura
              </button>
            </div>
          )}

          {showInfraForm && (
            <div className={s.form} style={{ marginBottom: 20 }}>
              <h2 className={s.sectionTitle}>
                {editingInfraId ? "Editar Infraestrutura" : "Nova Infraestrutura"}
              </h2>
              <div className={s.formGrid}>
                <div className={s.field}>
                  <label className={s.label}>Nome *</label>
                  <input
                    className={s.input}
                    value={infraForm.nome}
                    onChange={(e) => setInfraForm({ ...infraForm, nome: e.target.value })}
                    placeholder="Ex: Sala 1A"
                  />
                </div>
                <div className={s.field}>
                  <label className={s.label}>Tipo</label>
                  <select
                    className={s.input}
                    value={infraForm.tipo}
                    onChange={(e) => setInfraForm({ ...infraForm, tipo: e.target.value })}
                  >
                    {Object.entries(infraTipoLabel).map(([k, v]) => (
                      <option key={k} value={k}>{v}</option>
                    ))}
                  </select>
                </div>
                <div className={s.field}>
                  <label className={s.label}>Capacidade</label>
                  <input
                    className={s.input}
                    type="number"
                    min={0}
                    value={infraForm.capacidade}
                    onChange={(e) => setInfraForm({ ...infraForm, capacidade: e.target.value })}
                    placeholder="Nº de lugares"
                  />
                </div>
                <div className={s.field}>
                  <label className={s.label}>Estado</label>
                  <select
                    className={s.input}
                    value={infraForm.estado}
                    onChange={(e) => setInfraForm({ ...infraForm, estado: e.target.value })}
                  >
                    {Object.entries(estadoInfraLabel).map(([k, v]) => (
                      <option key={k} value={k}>{v}</option>
                    ))}
                  </select>
                </div>
                <div className={s.fieldFull}>
                  <label className={s.label}>Observações</label>
                  <input
                    className={s.input}
                    value={infraForm.observacoes}
                    onChange={(e) => setInfraForm({ ...infraForm, observacoes: e.target.value })}
                    placeholder="Notas adicionais..."
                  />
                </div>
              </div>
              <div className={s.formActions}>
                <button className={s.cancelBtn} onClick={() => setShowInfraForm(false)}>Cancelar</button>
                <button
                  className={s.primaryBtn}
                  onClick={handleSaveInfra}
                  disabled={infraSaving || !infraForm.nome.trim()}
                >
                  {infraSaving ? "A guardar..." : "Guardar"}
                </button>
              </div>
            </div>
          )}

          {infras.length === 0 ? (
            <p className={s.muted} style={{ textAlign: "center", padding: 32 }}>
              Nenhuma infraestrutura registada.
            </p>
          ) : (
            <div className={s.table}>
              <table>
                <thead>
                  <tr>
                    <th>Nome</th>
                    <th>Tipo</th>
                    <th>Capacidade</th>
                    <th>Estado</th>
                    <th>Observações</th>
                    {canManage && <th>Acções</th>}
                  </tr>
                </thead>
                <tbody>
                  {infras.map((infra) => (
                    <tr key={infra.id}>
                      <td style={{ fontWeight: 600 }}>{infra.nome}</td>
                      <td>{infraTipoLabel[infra.tipo] || infra.tipo}</td>
                      <td>{infra.capacidade ?? "—"}</td>
                      <td>
                        <span className={`${s.badge} ${estadoInfraBadge[infra.estado] || s.badgeGray}`}>
                          {estadoInfraLabel[infra.estado] || infra.estado}
                        </span>
                      </td>
                      <td className={s.muted}>{infra.observacoes || "—"}</td>
                      {canManage && (
                        <td>
                          <div style={{ display: "flex", gap: 6 }}>
                            <button
                              className={s.editBtn}
                              onClick={() => openEditInfra(infra)}
                              title="Editar"
                            >
                              <Edit2 size={14} />
                            </button>
                            <button
                              className={s.editBtn}
                              style={{ color: "#E53E3E", borderColor: "#E53E3E" }}
                              onClick={() => handleDeleteInfra(infra.id)}
                              title="Eliminar"
                            >
                              <Trash2 size={14} />
                            </button>
                          </div>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {infras.length > 0 && (
            <div className={s.statsGrid} style={{ marginTop: 20 }}>
              <div className={s.statCard}>
                <div>
                  <div className={s.statValue}>{infras.filter((i) => i.tipo === "sala_aula").length}</div>
                  <div className={s.statLabel}>Salas de Aula</div>
                </div>
              </div>
              <div className={s.statCard}>
                <div>
                  <div className={s.statValue}>{infras.reduce((sum, i) => sum + (i.capacidade || 0), 0)}</div>
                  <div className={s.statLabel}>Capacidade Total</div>
                </div>
              </div>
              <div className={s.statCard}>
                <div>
                  <div className={s.statValue}>{infras.filter((i) => i.estado === "operacional").length}</div>
                  <div className={s.statLabel}>Operacionais</div>
                </div>
              </div>
              <div className={s.statCard}>
                <div>
                  <div className={s.statValue}>{infras.filter((i) => i.estado !== "operacional").length}</div>
                  <div className={s.statLabel}>Em Reparação / Inop.</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab: Anos Letivos */}
      {tab === "anos" && (
        <div>
          {(!escola.anos_letivos || escola.anos_letivos.length === 0) ? (
            <p className={s.muted} style={{ textAlign: "center", padding: 32 }}>
              Nenhum ano letivo registado.
            </p>
          ) : (
            <div className={s.table}>
              <table>
                <thead>
                  <tr>
                    <th>Ano</th>
                    <th>Designação</th>
                    <th>Início</th>
                    <th>Fim</th>
                    <th>Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {escola.anos_letivos.map((al) => (
                    <tr key={al.id}>
                      <td style={{ fontWeight: 600 }}>{al.ano}</td>
                      <td>{al.designacao}</td>
                      <td>{new Date(al.data_inicio).toLocaleDateString("pt-AO")}</td>
                      <td>{new Date(al.data_fim).toLocaleDateString("pt-AO")}</td>
                      <td>
                        <span className={`${s.badge} ${al.ativo ? s.badgeGreen : s.badgeGray}`}>
                          {al.ativo ? "Ativo" : "Encerrado"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Tab: Configuração */}
      {tab === "config" && (
        <div className={s.form}>
          {escola.configuracao ? (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
              <InfoItem label="Nº de Períodos" value={String(escola.configuracao.num_periodos)} />
              <InfoItem label="Nota Máxima" value={String(escola.configuracao.nota_maxima)} />
              <InfoItem label="Nota Mínima de Aprovação" value={String(escola.configuracao.nota_minima_aprovacao)} />
            </div>
          ) : (
            <p className={s.muted}>Nenhuma configuração definida.</p>
          )}
        </div>
      )}
    </div>
  );
}

function InfoItem({ label, value, icon }: { label: string; value: string; icon?: React.ReactNode }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.5px", display: "flex", alignItems: "center", gap: 4 }}>
        {icon} {label}
      </span>
      <span style={{ fontSize: "0.95rem", color: "var(--text)", fontWeight: 500 }}>{value}</span>
    </div>
  );
}
