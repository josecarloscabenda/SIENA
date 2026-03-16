import { useEffect, useState } from "react";
import { ClipboardList, Plus, ArrowLeft, Trash2 } from "lucide-react";
import api from "@/shared/api/client";
import type {
  TurmaResponse,
  AvaliacaoResponse,
  NotaResponse,
  PaginatedResponse,
} from "@/shared/api/types";
import s from "@/shared/styles/common.module.css";

/* ── Avaliacao form ─────────────────────────── */

interface AvaliacaoForm {
  turma_id: string;
  disciplina_id: string;
  tipo: string;
  periodo: number;
  data: string;
  peso: number;
  nota_maxima: number;
}

const emptyAvaliacaoForm: AvaliacaoForm = {
  turma_id: "",
  disciplina_id: "",
  tipo: "teste",
  periodo: 1,
  data: "",
  peso: 1,
  nota_maxima: 20,
};

/* ── Nota row ───────────────────────────────── */

interface NotaRow {
  aluno_id: string;
  valor: number;
  observacoes: string;
}

const emptyNotaRow: NotaRow = { aluno_id: "", valor: 0, observacoes: "" };

/* ── Component ──────────────────────────────── */

export default function LancarNotas() {
  const [turmas, setTurmas] = useState<TurmaResponse[]>([]);
  const [selectedTurmaId, setSelectedTurmaId] = useState("");
  const [disciplinaId, setDisciplinaId] = useState("");

  const [avaliacoes, setAvaliacoes] = useState<AvaliacaoResponse[]>([]);
  const [loadingAval, setLoadingAval] = useState(false);

  // Detail: notas for a given avaliacao
  const [selectedAval, setSelectedAval] = useState<AvaliacaoResponse | null>(null);
  const [notas, setNotas] = useState<NotaResponse[]>([]);
  const [loadingNotas, setLoadingNotas] = useState(false);

  // Forms
  const [view, setView] = useState<"list" | "newAval" | "notas" | "lancarNotas">("list");
  const [avalForm, setAvalForm] = useState<AvaliacaoForm>(emptyAvaliacaoForm);
  const [notaRows, setNotaRows] = useState<NotaRow[]>([{ ...emptyNotaRow }]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  /* Fetch turmas */
  useEffect(() => {
    api
      .get<PaginatedResponse<TurmaResponse>>("/turmas?limit=100")
      .then(({ data }) => setTurmas(data.items))
      .catch(() => {});
  }, []);

  /* Fetch avaliacoes when turma changes */
  useEffect(() => {
    if (!selectedTurmaId) {
      setAvaliacoes([]);
      return;
    }
    setLoadingAval(true);
    const params = new URLSearchParams({ turma_id: selectedTurmaId, limit: "100" });
    if (disciplinaId) params.set("disciplina_id", disciplinaId);
    api
      .get<PaginatedResponse<AvaliacaoResponse>>(`/avaliacoes?${params}`)
      .then(({ data }) => setAvaliacoes(data.items))
      .catch(() => setAvaliacoes([]))
      .finally(() => setLoadingAval(false));
  }, [selectedTurmaId, disciplinaId]);

  /* View notas for an avaliacao */
  const openNotas = (aval: AvaliacaoResponse) => {
    setSelectedAval(aval);
    setLoadingNotas(true);
    setView("notas");
    api
      .get<NotaResponse[]>(`/avaliacoes/${aval.id}/notas`)
      .then(({ data }) => setNotas(data))
      .catch(() => setNotas([]))
      .finally(() => setLoadingNotas(false));
  };

  /* Create avaliacao */
  const openNewAval = () => {
    setAvalForm({
      ...emptyAvaliacaoForm,
      turma_id: selectedTurmaId,
      disciplina_id: disciplinaId,
    });
    setView("newAval");
    setError("");
  };

  const handleSubmitAval = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      await api.post("/avaliacoes", {
        turma_id: avalForm.turma_id,
        disciplina_id: avalForm.disciplina_id,
        tipo: avalForm.tipo,
        periodo: Number(avalForm.periodo),
        data: avalForm.data,
        peso: Number(avalForm.peso),
        nota_maxima: Number(avalForm.nota_maxima),
      });
      setView("list");
      // Refresh
      const params = new URLSearchParams({ turma_id: selectedTurmaId, limit: "100" });
      const { data } = await api.get<PaginatedResponse<AvaliacaoResponse>>(
        `/avaliacoes?${params}`,
      );
      setAvaliacoes(data.items);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao criar avaliação.");
    } finally {
      setSaving(false);
    }
  };

  /* Lancar notas */
  const openLancarNotas = () => {
    setNotaRows([{ ...emptyNotaRow }]);
    setView("lancarNotas");
    setError("");
  };

  const addNotaRow = () => setNotaRows([...notaRows, { ...emptyNotaRow }]);

  const removeNotaRow = (idx: number) => {
    if (notaRows.length <= 1) return;
    setNotaRows(notaRows.filter((_, i) => i !== idx));
  };

  const updateNotaRow = (idx: number, field: keyof NotaRow, value: string | number) => {
    setNotaRows(
      notaRows.map((row, i) => (i === idx ? { ...row, [field]: value } : row)),
    );
  };

  const handleSubmitNotas = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAval) return;
    setSaving(true);
    setError("");
    try {
      await api.post(`/avaliacoes/${selectedAval.id}/notas`, {
        notas: notaRows.map((r) => ({
          aluno_id: r.aluno_id,
          valor: Number(r.valor),
          observacoes: r.observacoes || null,
        })),
      });
      // Refresh notas view
      openNotas(selectedAval);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao lançar notas.");
    } finally {
      setSaving(false);
    }
  };

  const tipoLabel: Record<string, string> = {
    teste: "Teste",
    trabalho: "Trabalho",
    exame: "Exame",
    oral: "Oral",
  };

  /* ── New Avaliacao Form ───────────────────── */
  if (view === "newAval") {
    return (
      <div>
        <button className={s.backBtn} onClick={() => setView("list")}>
          <ArrowLeft size={16} /> Voltar
        </button>
        <h1 className={s.pageTitle}>Nova Avaliação</h1>

        {error && <div className={s.error}>{error}</div>}

        <form className={s.form} onSubmit={handleSubmitAval}>
          <div className={s.formGrid}>
            <div className={s.field}>
              <label className={s.label}>Turma</label>
              <select
                className={s.input}
                required
                value={avalForm.turma_id}
                onChange={(e) =>
                  setAvalForm({ ...avalForm, turma_id: e.target.value })
                }
              >
                <option value="">Seleccionar...</option>
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
                value={avalForm.disciplina_id}
                onChange={(e) =>
                  setAvalForm({ ...avalForm, disciplina_id: e.target.value })
                }
              />
            </div>
            <div className={s.field}>
              <label className={s.label}>Tipo</label>
              <select
                className={s.input}
                value={avalForm.tipo}
                onChange={(e) =>
                  setAvalForm({ ...avalForm, tipo: e.target.value })
                }
              >
                <option value="teste">Teste</option>
                <option value="trabalho">Trabalho</option>
                <option value="exame">Exame</option>
                <option value="oral">Oral</option>
              </select>
            </div>
            <div className={s.field}>
              <label className={s.label}>Período</label>
              <select
                className={s.input}
                value={avalForm.periodo}
                onChange={(e) =>
                  setAvalForm({ ...avalForm, periodo: Number(e.target.value) })
                }
              >
                <option value={1}>1.º Período</option>
                <option value={2}>2.º Período</option>
                <option value={3}>3.º Período</option>
              </select>
            </div>
            <div className={s.field}>
              <label className={s.label}>Data</label>
              <input
                className={s.input}
                type="date"
                required
                value={avalForm.data}
                onChange={(e) =>
                  setAvalForm({ ...avalForm, data: e.target.value })
                }
              />
            </div>
            <div className={s.field}>
              <label className={s.label}>Peso (0 a 1)</label>
              <input
                className={s.input}
                type="number"
                step="0.1"
                min="0"
                max="1"
                required
                value={avalForm.peso}
                onChange={(e) =>
                  setAvalForm({ ...avalForm, peso: Number(e.target.value) })
                }
              />
            </div>
            <div className={s.field}>
              <label className={s.label}>Nota Máxima</label>
              <input
                className={s.input}
                type="number"
                required
                value={avalForm.nota_maxima}
                onChange={(e) =>
                  setAvalForm({ ...avalForm, nota_maxima: Number(e.target.value) })
                }
              />
            </div>
          </div>
          <div className={s.formActions}>
            <button
              type="button"
              className={s.cancelBtn}
              onClick={() => setView("list")}
            >
              Cancelar
            </button>
            <button type="submit" className={s.primaryBtn} disabled={saving}>
              {saving ? "A guardar..." : "Criar Avaliação"}
            </button>
          </div>
        </form>
      </div>
    );
  }

  /* ── View Notas ───────────────────────────── */
  if (view === "notas" && selectedAval) {
    return (
      <div>
        <button className={s.backBtn} onClick={() => setView("list")}>
          <ArrowLeft size={16} /> Voltar
        </button>
        <div className={s.pageHeader}>
          <div>
            <h1 className={s.pageTitle}>
              Notas — {tipoLabel[selectedAval.tipo] || selectedAval.tipo}
            </h1>
            <p className={s.subtitle}>
              Data: {selectedAval.data} &middot; Nota Máxima:{" "}
              {selectedAval.nota_maxima}
            </p>
          </div>
          <button className={s.addBtn} onClick={openLancarNotas}>
            <Plus size={18} />
            Lançar Notas
          </button>
        </div>

        {loadingNotas ? (
          <p className={s.muted}>A carregar...</p>
        ) : notas.length === 0 ? (
          <p className={s.muted}>Nenhuma nota lançada para esta avaliação.</p>
        ) : (
          <div className={s.table}>
            <table>
              <thead>
                <tr>
                  <th>Aluno ID</th>
                  <th>Valor</th>
                  <th>Observações</th>
                </tr>
              </thead>
              <tbody>
                {notas.map((n) => (
                  <tr key={n.id}>
                    <td style={{ fontFamily: "monospace", fontSize: "0.8rem" }}>
                      {n.aluno_id}
                    </td>
                    <td>
                      <span
                        className={`${s.badge} ${
                          n.valor >= selectedAval.nota_maxima * 0.5
                            ? s.badgeGreen
                            : s.badgeRed
                        }`}
                      >
                        {n.valor}
                      </span>
                    </td>
                    <td>{n.observacoes || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    );
  }

  /* ── Lancar Notas Form ────────────────────── */
  if (view === "lancarNotas" && selectedAval) {
    return (
      <div>
        <button
          className={s.backBtn}
          onClick={() => openNotas(selectedAval)}
        >
          <ArrowLeft size={16} /> Voltar
        </button>
        <h1 className={s.pageTitle}>Lançar Notas</h1>
        <p className={s.subtitle} style={{ marginBottom: 16 }}>
          {tipoLabel[selectedAval.tipo] || selectedAval.tipo} &middot; Nota
          Máxima: {selectedAval.nota_maxima}
        </p>

        {error && <div className={s.error}>{error}</div>}

        <form className={s.form} onSubmit={handleSubmitNotas}>
          {notaRows.map((row, idx) => (
            <div
              key={idx}
              className={s.formGrid}
              style={{ marginBottom: 12, alignItems: "flex-end" }}
            >
              <div className={s.field}>
                <label className={s.label}>Aluno ID</label>
                <input
                  className={s.input}
                  required
                  placeholder="UUID do aluno"
                  value={row.aluno_id}
                  onChange={(e) =>
                    updateNotaRow(idx, "aluno_id", e.target.value)
                  }
                />
              </div>
              <div className={s.field}>
                <label className={s.label}>Valor</label>
                <input
                  className={s.input}
                  type="number"
                  step="0.1"
                  min="0"
                  max={selectedAval.nota_maxima}
                  required
                  value={row.valor}
                  onChange={(e) =>
                    updateNotaRow(idx, "valor", Number(e.target.value))
                  }
                />
              </div>
              <div className={s.field}>
                <label className={s.label}>Observações</label>
                <input
                  className={s.input}
                  value={row.observacoes}
                  onChange={(e) =>
                    updateNotaRow(idx, "observacoes", e.target.value)
                  }
                />
              </div>
              <div>
                <button
                  type="button"
                  className={s.cancelBtn}
                  style={{ padding: "10px 12px" }}
                  onClick={() => removeNotaRow(idx)}
                  disabled={notaRows.length <= 1}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}

          <button
            type="button"
            className={s.editBtn}
            style={{ marginBottom: 16 }}
            onClick={addNotaRow}
          >
            <Plus size={14} /> Adicionar Linha
          </button>

          <div className={s.formActions}>
            <button
              type="button"
              className={s.cancelBtn}
              onClick={() => openNotas(selectedAval)}
            >
              Cancelar
            </button>
            <button type="submit" className={s.primaryBtn} disabled={saving}>
              {saving ? "A guardar..." : "Submeter Notas"}
            </button>
          </div>
        </form>
      </div>
    );
  }

  /* ── Main List View ───────────────────────── */
  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>Lançar Notas</h1>
          <p className={s.subtitle}>Avaliações e notas dos alunos</p>
        </div>
        {selectedTurmaId && (
          <button className={s.addBtn} onClick={openNewAval}>
            <Plus size={18} />
            Nova Avaliação
          </button>
        )}
      </div>

      {/* Selectors */}
      <div className={s.section}>
        <div className={s.formGrid} style={{ maxWidth: 600 }}>
          <div className={s.field}>
            <label className={s.label}>Turma</label>
            <select
              className={s.input}
              value={selectedTurmaId}
              onChange={(e) => setSelectedTurmaId(e.target.value)}
            >
              <option value="">-- Seleccionar Turma --</option>
              {turmas.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.nome} ({t.classe})
                </option>
              ))}
            </select>
          </div>
          <div className={s.field}>
            <label className={s.label}>Disciplina ID (opcional)</label>
            <input
              className={s.input}
              placeholder="Filtrar por disciplina..."
              value={disciplinaId}
              onChange={(e) => setDisciplinaId(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Avaliacoes table */}
      {!selectedTurmaId ? (
        <div className={s.emptyState}>
          <div className={s.emptyIcon}>
            <ClipboardList size={48} />
          </div>
          <p>Seleccione uma turma para ver as avaliações.</p>
        </div>
      ) : loadingAval ? (
        <p className={s.muted}>A carregar...</p>
      ) : avaliacoes.length === 0 ? (
        <p className={s.muted}>Nenhuma avaliação encontrada.</p>
      ) : (
        <div className={s.table}>
          <table>
            <thead>
              <tr>
                <th>Tipo</th>
                <th>Período</th>
                <th>Data</th>
                <th>Peso</th>
                <th>Nota Máxima</th>
                <th>Acções</th>
              </tr>
            </thead>
            <tbody>
              {avaliacoes.map((aval) => (
                <tr key={aval.id}>
                  <td>
                    <span className={`${s.badge} ${s.badgeBlue}`}>
                      {tipoLabel[aval.tipo] || aval.tipo}
                    </span>
                  </td>
                  <td>{aval.periodo}.º</td>
                  <td>{aval.data}</td>
                  <td>{aval.peso}</td>
                  <td>{aval.nota_maxima}</td>
                  <td>
                    <button
                      className={s.editBtn}
                      onClick={() => openNotas(aval)}
                    >
                      Ver Notas
                    </button>
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
