import { useEffect, useState } from "react";
import { Plus, Search, LayoutGrid } from "lucide-react";
import api from "@/shared/api/client";
import type { TurmaResponse, PaginatedResponse } from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

interface TurmaForm {
  nome: string;
  classe: string;
  turno: string;
  ano_letivo_id: string;
  capacidade_max: number;
  professor_regente_id: string;
  sala: string;
}

const emptyForm: TurmaForm = {
  nome: "",
  classe: "",
  turno: "matutino",
  ano_letivo_id: "",
  capacidade_max: 40,
  professor_regente_id: "",
  sala: "",
};

const turnoLabel: Record<string, string> = {
  matutino: "Matutino",
  vespertino: "Vespertino",
  nocturno: "Nocturno",
};

export default function Turmas() {
  const { hasRole } = useAuth();
  const [turmas, setTurmas] = useState<TurmaResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<TurmaForm>(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const canManage = hasRole("super_admin", "diretor", "secretaria");

  const fetchTurmas = () => {
    setLoading(true);
    const params = new URLSearchParams({ offset: "0", limit: "50" });
    api
      .get<PaginatedResponse<TurmaResponse>>(`/turmas?${params}`)
      .then(({ data }) => {
        setTurmas(data.items);
        setTotal(data.total);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchTurmas();
  }, []);

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
      await api.post("/turmas", {
        ...form,
        capacidade_max: Number(form.capacidade_max),
      });
      setShowForm(false);
      fetchTurmas();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao criar turma.");
    } finally {
      setSaving(false);
    }
  };

  const filtered = turmas.filter((t) => {
    const q = search.toLowerCase();
    return (
      t.nome.toLowerCase().includes(q) ||
      t.classe.toLowerCase().includes(q) ||
      (t.sala?.toLowerCase().includes(q) ?? false)
    );
  });

  if (showForm) {
    return (
      <div>
        <button className={s.backBtn} onClick={() => setShowForm(false)}>
          &larr; Voltar
        </button>
        <h1 className={s.pageTitle}>Nova Turma</h1>

        {error && <div className={s.error}>{error}</div>}

        <form className={s.form} onSubmit={handleSubmit}>
          <div className={s.formGrid}>
            <div className={s.field}>
              <label className={s.label}>Nome</label>
              <input className={s.input} required value={form.nome} onChange={(e) => setForm({ ...form, nome: e.target.value })} />
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
            <div className={s.field}>
              <label className={s.label}>Ano Lectivo ID</label>
              <input className={s.input} required placeholder="UUID do ano lectivo" value={form.ano_letivo_id} onChange={(e) => setForm({ ...form, ano_letivo_id: e.target.value })} />
            </div>
            <div className={s.field}>
              <label className={s.label}>Capacidade Maxima</label>
              <input className={s.input} type="number" required value={form.capacidade_max} onChange={(e) => setForm({ ...form, capacidade_max: Number(e.target.value) })} />
            </div>
            <div className={s.field}>
              <label className={s.label}>Professor Regente ID</label>
              <input className={s.input} required placeholder="UUID do professor" value={form.professor_regente_id} onChange={(e) => setForm({ ...form, professor_regente_id: e.target.value })} />
            </div>
            <div className={s.field}>
              <label className={s.label}>Sala</label>
              <input className={s.input} value={form.sala} onChange={(e) => setForm({ ...form, sala: e.target.value })} />
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
          <h1 className={s.pageTitle}>Turmas</h1>
          <p className={s.subtitle}>{total} turma(s) registada(s)</p>
        </div>
        {canManage && (
          <button className={s.addBtn} onClick={openCreate}>
            <Plus size={18} />
            Nova Turma
          </button>
        )}
      </div>

      <div className={s.searchBar}>
        <Search size={18} color="var(--text-muted)" />
        <input
          type="text"
          placeholder="Pesquisar por nome, classe ou sala..."
          className={s.searchInput}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <p className={s.muted}>A carregar...</p>
      ) : filtered.length === 0 ? (
        <p className={s.muted}>Nenhuma turma encontrada.</p>
      ) : (
        <div className={s.table}>
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>Classe</th>
                <th>Turno</th>
                <th>Capacidade</th>
                <th>Sala</th>
                {canManage && <th>Accoes</th>}
              </tr>
            </thead>
            <tbody>
              {filtered.map((turma) => (
                <tr key={turma.id}>
                  <td>
                    <div className={s.nameCell}>
                      <LayoutGrid size={16} />
                      {turma.nome}
                    </div>
                  </td>
                  <td>{turma.classe}</td>
                  <td>{turnoLabel[turma.turno] || turma.turno}</td>
                  <td>{turma.capacidade_max}</td>
                  <td>{turma.sala || "—"}</td>
                  {canManage && (
                    <td>
                      <button className={s.editBtn}>
                        Ver
                      </button>
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
