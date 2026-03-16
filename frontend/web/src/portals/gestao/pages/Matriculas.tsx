import { useEffect, useState } from "react";
import { Plus, ClipboardList, Check, X } from "lucide-react";
import api from "@/shared/api/client";
import type { MatriculaResponse, PaginatedResponse } from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

type EstadoFilter = "" | "pendente" | "aprovada" | "rejeitada";

interface MatriculaForm {
  aluno_id: string;
  ano_letivo_id: string;
  classe: string;
  turno: string;
  observacoes: string;
}

const emptyForm: MatriculaForm = {
  aluno_id: "",
  ano_letivo_id: "",
  classe: "",
  turno: "matutino",
  observacoes: "",
};

const estadoBadge: Record<string, string> = {
  pendente: s.badgeYellow,
  aprovada: s.badgeGreen,
  rejeitada: s.badgeRed,
};

const estadoLabel: Record<string, string> = {
  pendente: "Pendente",
  aprovada: "Aprovada",
  rejeitada: "Rejeitada",
};

const turnoLabel: Record<string, string> = {
  matutino: "Matutino",
  vespertino: "Vespertino",
  nocturno: "Nocturno",
};

export default function Matriculas() {
  const { hasRole } = useAuth();
  const [matriculas, setMatriculas] = useState<MatriculaResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [estadoFilter, setEstadoFilter] = useState<EstadoFilter>("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<MatriculaForm>(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [rejectId, setRejectId] = useState<string | null>(null);
  const [rejectMotivo, setRejectMotivo] = useState("");

  const canManage = hasRole("super_admin", "diretor", "secretaria");

  const fetchMatriculas = () => {
    setLoading(true);
    const params = new URLSearchParams({ offset: "0", limit: "50" });
    if (estadoFilter) params.set("estado", estadoFilter);
    api
      .get<PaginatedResponse<MatriculaResponse>>(`/matriculas?${params}`)
      .then(({ data }) => {
        setMatriculas(data.items);
        setTotal(data.total);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchMatriculas();
  }, [estadoFilter]);

  const openCreate = () => {
    setForm(emptyForm);
    setShowForm(true);
    setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      await api.post("/matriculas", form);
      setShowForm(false);
      fetchMatriculas();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao criar matricula.");
    } finally {
      setSaving(false);
    }
  };

  const handleAprovar = async (id: string) => {
    try {
      await api.post(`/matriculas/${id}/aprovar`);
      fetchMatriculas();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Erro ao aprovar matricula.");
    }
  };

  const handleRejeitar = async () => {
    if (!rejectId) return;
    try {
      await api.post(`/matriculas/${rejectId}/rejeitar`, { motivo: rejectMotivo });
      setRejectId(null);
      setRejectMotivo("");
      fetchMatriculas();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Erro ao rejeitar matricula.");
    }
  };

  const tabs: { label: string; value: EstadoFilter }[] = [
    { label: "Todas", value: "" },
    { label: "Pendentes", value: "pendente" },
    { label: "Aprovadas", value: "aprovada" },
    { label: "Rejeitadas", value: "rejeitada" },
  ];

  if (showForm) {
    return (
      <div>
        <button className={s.backBtn} onClick={() => setShowForm(false)}>
          &larr; Voltar
        </button>
        <h1 className={s.pageTitle}>Nova Matricula</h1>

        {error && <div className={s.error}>{error}</div>}

        <form className={s.form} onSubmit={handleSubmit}>
          <div className={s.formGrid}>
            <div className={s.field}>
              <label className={s.label}>Aluno ID</label>
              <input className={s.input} required placeholder="UUID do aluno" value={form.aluno_id} onChange={(e) => setForm({ ...form, aluno_id: e.target.value })} />
            </div>
            <div className={s.field}>
              <label className={s.label}>Ano Lectivo ID</label>
              <input className={s.input} required placeholder="UUID do ano lectivo" value={form.ano_letivo_id} onChange={(e) => setForm({ ...form, ano_letivo_id: e.target.value })} />
            </div>
            <div className={s.field}>
              <label className={s.label}>Classe</label>
              <input className={s.input} required value={form.classe} onChange={(e) => setForm({ ...form, classe: e.target.value })} />
            </div>
            <div className={s.field}>
              <label className={s.label}>Turno</label>
              <select className={s.input} value={form.turno} onChange={(e) => setForm({ ...form, turno: e.target.value })}>
                <option value="matutino">Matutino</option>
                <option value="vespertino">Vespertino</option>
                <option value="nocturno">Nocturno</option>
              </select>
            </div>
            <div className={s.fieldFull}>
              <label className={s.label}>Observacoes</label>
              <input className={s.input} value={form.observacoes} onChange={(e) => setForm({ ...form, observacoes: e.target.value })} />
            </div>
          </div>
          <div className={s.formActions}>
            <button type="button" className={s.cancelBtn} onClick={() => setShowForm(false)}>Cancelar</button>
            <button type="submit" className={s.primaryBtn} disabled={saving}>{saving ? "A guardar..." : "Guardar"}</button>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>Matriculas</h1>
          <p className={s.subtitle}>{total} matricula(s)</p>
        </div>
        {canManage && (
          <button className={s.addBtn} onClick={openCreate}>
            <Plus size={18} />
            Nova Matricula
          </button>
        )}
      </div>

      <div className={s.tabs}>
        {tabs.map((tab) => (
          <button
            key={tab.value}
            className={`${s.tab} ${estadoFilter === tab.value ? s.tabActive : ""}`}
            onClick={() => setEstadoFilter(tab.value)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Reject modal */}
      {rejectId && (
        <div className={s.form} style={{ marginBottom: 20 }}>
          <h3 style={{ marginBottom: 12, fontSize: "0.95rem" }}>Motivo da Rejeicao</h3>
          <input
            className={s.input}
            placeholder="Indique o motivo..."
            value={rejectMotivo}
            onChange={(e) => setRejectMotivo(e.target.value)}
            style={{ width: "100%", marginBottom: 12 }}
          />
          <div className={s.formActions}>
            <button type="button" className={s.cancelBtn} onClick={() => { setRejectId(null); setRejectMotivo(""); }}>Cancelar</button>
            <button
              type="button"
              className={s.primaryBtn}
              style={{ background: "#E53E3E" }}
              onClick={handleRejeitar}
              disabled={!rejectMotivo.trim()}
            >
              Confirmar Rejeicao
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <p className={s.muted}>A carregar...</p>
      ) : matriculas.length === 0 ? (
        <p className={s.muted}>Nenhuma matricula encontrada.</p>
      ) : (
        <div className={s.table}>
          <table>
            <thead>
              <tr>
                <th>Aluno ID</th>
                <th>Classe</th>
                <th>Turno</th>
                <th>Estado</th>
                <th>Data Pedido</th>
                {canManage && <th>Accoes</th>}
              </tr>
            </thead>
            <tbody>
              {matriculas.map((mat) => (
                <tr key={mat.id}>
                  <td>
                    <div className={s.nameCell}>
                      <ClipboardList size={16} />
                      {mat.aluno_id.slice(0, 8)}...
                    </div>
                  </td>
                  <td>{mat.classe}</td>
                  <td>{turnoLabel[mat.turno] || mat.turno}</td>
                  <td>
                    <span className={`${s.badge} ${estadoBadge[mat.estado] || s.badgeGray}`}>
                      {estadoLabel[mat.estado] || mat.estado}
                    </span>
                  </td>
                  <td>{new Date(mat.data_pedido).toLocaleDateString("pt-AO")}</td>
                  {canManage && (
                    <td>
                      {mat.estado === "pendente" ? (
                        <div style={{ display: "flex", gap: 6 }}>
                          <button
                            className={s.editBtn}
                            style={{ color: "#38A169", borderColor: "#38A169" }}
                            onClick={() => handleAprovar(mat.id)}
                            title="Aprovar"
                          >
                            <Check size={14} />
                          </button>
                          <button
                            className={s.editBtn}
                            style={{ color: "#E53E3E", borderColor: "#E53E3E" }}
                            onClick={() => setRejectId(mat.id)}
                            title="Rejeitar"
                          >
                            <X size={14} />
                          </button>
                        </div>
                      ) : (
                        <span className={s.muted}>—</span>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
