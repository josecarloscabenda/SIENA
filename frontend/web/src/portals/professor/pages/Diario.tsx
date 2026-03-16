import { useEffect, useState } from "react";
import { BookOpen, Plus, ArrowLeft } from "lucide-react";
import api from "@/shared/api/client";
import type {
  TurmaResponse,
  DiarioClasseResponse,
  PaginatedResponse,
} from "@/shared/api/types";
import s from "@/shared/styles/common.module.css";

interface DiarioForm {
  turma_id: string;
  disciplina_id: string;
  data_aula: string;
  conteudo: string;
  sumario: string;
  observacoes: string;
}

const emptyForm: DiarioForm = {
  turma_id: "",
  disciplina_id: "",
  data_aula: "",
  conteudo: "",
  sumario: "",
  observacoes: "",
};

export default function Diario() {
  const [turmas, setTurmas] = useState<TurmaResponse[]>([]);
  const [selectedTurmaId, setSelectedTurmaId] = useState("");
  const [entries, setEntries] = useState<DiarioClasseResponse[]>([]);
  const [loading, setLoading] = useState(false);

  // Form state
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<DiarioForm>(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get<PaginatedResponse<TurmaResponse>>("/turmas?limit=100")
      .then(({ data }) => setTurmas(data.items))
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!selectedTurmaId) {
      setEntries([]);
      return;
    }
    setLoading(true);
    api
      .get<PaginatedResponse<DiarioClasseResponse>>(
        `/diario?turma_id=${selectedTurmaId}&limit=20`,
      )
      .then(({ data }) => setEntries(data.items))
      .catch(() => setEntries([]))
      .finally(() => setLoading(false));
  }, [selectedTurmaId]);

  const openCreate = () => {
    setForm({ ...emptyForm, turma_id: selectedTurmaId });
    setShowForm(true);
    setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      await api.post("/diario", {
        turma_id: form.turma_id,
        disciplina_id: form.disciplina_id,
        data_aula: form.data_aula,
        conteudo: form.conteudo,
        sumario: form.sumario,
        observacoes: form.observacoes || null,
        presencas: [],
      });
      setShowForm(false);
      // Refresh entries
      if (selectedTurmaId) {
        const { data } = await api.get<PaginatedResponse<DiarioClasseResponse>>(
          `/diario?turma_id=${selectedTurmaId}&limit=20`,
        );
        setEntries(data.items);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao registar aula.");
    } finally {
      setSaving(false);
    }
  };

  if (showForm) {
    return (
      <div>
        <button className={s.backBtn} onClick={() => setShowForm(false)}>
          <ArrowLeft size={16} /> Voltar
        </button>
        <h1 className={s.pageTitle}>Registar Aula</h1>

        {error && <div className={s.error}>{error}</div>}

        <form className={s.form} onSubmit={handleSubmit}>
          <div className={s.formGrid}>
            <div className={s.field}>
              <label className={s.label}>Turma</label>
              <select
                className={s.input}
                required
                value={form.turma_id}
                onChange={(e) => setForm({ ...form, turma_id: e.target.value })}
              >
                <option value="">Seleccionar turma...</option>
                {turmas.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.nome} ({t.classe})
                  </option>
                ))}
              </select>
            </div>
            <div className={s.field}>
              <label className={s.label}>Disciplina ID</label>
              <input
                className={s.input}
                required
                placeholder="UUID da disciplina"
                value={form.disciplina_id}
                onChange={(e) =>
                  setForm({ ...form, disciplina_id: e.target.value })
                }
              />
            </div>
            <div className={s.field}>
              <label className={s.label}>Data da Aula</label>
              <input
                className={s.input}
                type="date"
                required
                value={form.data_aula}
                onChange={(e) =>
                  setForm({ ...form, data_aula: e.target.value })
                }
              />
            </div>
            <div className={s.field}>
              <label className={s.label}>Sumário</label>
              <input
                className={s.input}
                required
                value={form.sumario}
                onChange={(e) => setForm({ ...form, sumario: e.target.value })}
              />
            </div>
            <div className={s.fieldFull}>
              <label className={s.label}>Conteúdo</label>
              <textarea
                className={s.input}
                required
                rows={4}
                value={form.conteudo}
                onChange={(e) =>
                  setForm({ ...form, conteudo: e.target.value })
                }
              />
            </div>
            <div className={s.fieldFull}>
              <label className={s.label}>Observações</label>
              <textarea
                className={s.input}
                rows={3}
                value={form.observacoes}
                onChange={(e) =>
                  setForm({ ...form, observacoes: e.target.value })
                }
              />
            </div>
          </div>
          <div className={s.formActions}>
            <button
              type="button"
              className={s.cancelBtn}
              onClick={() => setShowForm(false)}
            >
              Cancelar
            </button>
            <button type="submit" className={s.primaryBtn} disabled={saving}>
              {saving ? "A guardar..." : "Registar"}
            </button>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>Diário de Classe</h1>
          <p className={s.subtitle}>Registo de aulas e presenças</p>
        </div>
        {selectedTurmaId && (
          <button className={s.addBtn} onClick={openCreate}>
            <Plus size={18} />
            Registar Aula
          </button>
        )}
      </div>

      {/* Turma selector */}
      <div className={s.section}>
        <div className={s.field} style={{ maxWidth: 400 }}>
          <label className={s.label}>Seleccionar Turma</label>
          <select
            className={s.input}
            value={selectedTurmaId}
            onChange={(e) => setSelectedTurmaId(e.target.value)}
          >
            <option value="">-- Seleccionar --</option>
            {turmas.map((t) => (
              <option key={t.id} value={t.id}>
                {t.nome} ({t.classe})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Entries */}
      {!selectedTurmaId ? (
        <div className={s.emptyState}>
          <div className={s.emptyIcon}>
            <BookOpen size={48} />
          </div>
          <p>Seleccione uma turma para ver o diário de classe.</p>
        </div>
      ) : loading ? (
        <p className={s.muted}>A carregar...</p>
      ) : entries.length === 0 ? (
        <p className={s.muted}>Nenhum registo encontrado para esta turma.</p>
      ) : (
        <div className={s.table}>
          <table>
            <thead>
              <tr>
                <th>Data</th>
                <th>Disciplina ID</th>
                <th>Sumário</th>
                <th>Presenças</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => (
                <tr key={entry.id}>
                  <td>{entry.data_aula}</td>
                  <td style={{ fontFamily: "monospace", fontSize: "0.8rem" }}>
                    {entry.disciplina_id}
                  </td>
                  <td>{entry.sumario}</td>
                  <td>
                    <span className={`${s.badge} ${s.badgeBlue}`}>
                      {entry.presencas.length}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
