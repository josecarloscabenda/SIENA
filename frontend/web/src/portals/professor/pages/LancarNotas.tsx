import { useEffect, useState } from "react";
import { ClipboardList, Plus, ArrowLeft } from "lucide-react";
import api from "@/shared/api/client";
import { useAuth } from "@/shared/hooks/useAuth";
import type {
  AvaliacaoResponse,
  NotaResponse,
  PaginatedResponse,
  ProfessorDisciplinaItem,
  ProfessorTurmaItem,
  TurmaAlunoItem,
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

/* ── Nota row (preenchimento por aluno da turma) ────── */

interface NotaRow {
  aluno_id: string;
  matricula_id: string;
  nome: string;
  n_processo: string;
  valor: string;          // string para permitir input vazio
  observacoes: string;
}

/* ── Component ──────────────────────────────── */

export default function LancarNotas() {
  const { user } = useAuth();
  const professorId = user?.professor_id ?? null;

  const [turmas, setTurmas] = useState<ProfessorTurmaItem[]>([]);
  const [selectedTurmaId, setSelectedTurmaId] = useState("");
  const [disciplinaId, setDisciplinaId] = useState("");
  const [disciplinas, setDisciplinas] = useState<ProfessorDisciplinaItem[]>([]);

  const [avaliacoes, setAvaliacoes] = useState<AvaliacaoResponse[]>([]);
  const [loadingAval, setLoadingAval] = useState(false);

  // Detail: notas for a given avaliacao
  const [selectedAval, setSelectedAval] = useState<AvaliacaoResponse | null>(null);
  const [notas, setNotas] = useState<NotaResponse[]>([]);
  const [loadingNotas, setLoadingNotas] = useState(false);

  // Forms
  const [view, setView] = useState<"list" | "newAval" | "notas" | "lancarNotas">("list");
  const [avalForm, setAvalForm] = useState<AvaliacaoForm>(emptyAvaliacaoForm);
  const [notaRows, setNotaRows] = useState<NotaRow[]>([]);
  const [loadingAlunos, setLoadingAlunos] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  /* Carregar turmas do professor logado */
  useEffect(() => {
    if (!professorId) {
      setTurmas([]);
      return;
    }
    api
      .get<ProfessorTurmaItem[]>(`/professores/${professorId}/turmas`)
      .then(({ data }) => setTurmas(data))
      .catch(() => setTurmas([]));
  }, [professorId]);

  /* Cascata: ao mudar turma, recarrega disciplinas filtradas e limpa selecção de disciplina */
  useEffect(() => {
    setDisciplinaId("");
    if (!professorId || !selectedTurmaId) {
      setDisciplinas([]);
      return;
    }
    api
      .get<ProfessorDisciplinaItem[]>(
        `/professores/${professorId}/disciplinas?turma_id=${selectedTurmaId}`,
      )
      .then(({ data }) => setDisciplinas(data))
      .catch(() => setDisciplinas([]));
  }, [professorId, selectedTurmaId]);

  /* Fetch avaliacoes when turma/disciplina changes */
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

  /* Lancar notas — carrega alunos da turma automaticamente */
  const openLancarNotas = async () => {
    if (!selectedAval) return;
    setView("lancarNotas");
    setError("");
    setLoadingAlunos(true);
    try {
      const { data } = await api.get<TurmaAlunoItem[]>(
        `/turmas/${selectedAval.turma_id}/alunos`,
      );
      // Pré-popula com notas existentes (caso já tenham sido lançadas)
      const existing = new Map(notas.map((n) => [n.aluno_id, n]));
      setNotaRows(
        data.map((a) => {
          const prev = existing.get(a.aluno_id);
          return {
            aluno_id: a.aluno_id,
            matricula_id: a.matricula_id,
            nome: a.nome,
            n_processo: a.n_processo,
            valor: prev ? String(prev.valor) : "",
            observacoes: prev?.observacoes ?? "",
          };
        }),
      );
    } catch {
      setError("Erro ao carregar alunos da turma");
      setNotaRows([]);
    } finally {
      setLoadingAlunos(false);
    }
  };

  const updateNotaRow = (idx: number, field: "valor" | "observacoes", value: string) => {
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
      // Só submete linhas com valor preenchido
      const payload = notaRows
        .filter((r) => r.valor !== "")
        .map((r) => ({
          aluno_id: r.aluno_id,
          valor: Number(r.valor),
          observacoes: r.observacoes || null,
        }));
      if (payload.length === 0) {
        setError("Preencha pelo menos uma nota.");
        setSaving(false);
        return;
      }
      await api.post(`/avaliacoes/${selectedAval.id}/notas`, { notas: payload });
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
                  setAvalForm({ ...avalForm, turma_id: e.target.value, disciplina_id: "" })
                }
              >
                <option value="">Seleccionar...</option>
                {turmas.map((t) => (
                  <option key={t.turma_id} value={t.turma_id}>
                    {t.nome} ({t.classe}) {t.is_regente ? "★ regente" : ""}
                  </option>
                ))}
              </select>
            </div>
            <div className={s.field}>
              <label className={s.label}>Disciplina</label>
              <select
                className={s.input}
                required
                disabled={!avalForm.turma_id || disciplinas.length === 0}
                value={avalForm.disciplina_id}
                onChange={(e) =>
                  setAvalForm({ ...avalForm, disciplina_id: e.target.value })
                }
              >
                <option value="">
                  {avalForm.turma_id
                    ? disciplinas.length === 0
                      ? "Sem disciplinas nesta turma"
                      : "Seleccionar disciplina..."
                    : "Seleccione primeiro a turma"}
                </option>
                {disciplinas.map((d) => (
                  <option key={d.disciplina_id} value={d.disciplina_id}>
                    {d.nome} ({d.codigo})
                  </option>
                ))}
              </select>
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
                  <th>Aluno</th>
                  <th>Nº Processo</th>
                  <th>Valor</th>
                  <th>Observações</th>
                </tr>
              </thead>
              <tbody>
                {notas.map((n) => (
                  <tr key={n.id}>
                    <td>
                      {n.aluno_nome || (
                        <span className={s.muted}>Aluno {n.aluno_id.slice(0, 8)}</span>
                      )}
                    </td>
                    <td>{n.aluno_n_processo || <span className={s.muted}>—</span>}</td>
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

  /* ── Lancar Notas Form (linha por aluno da turma) ────── */
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
          Máxima: {selectedAval.nota_maxima} &middot; {notaRows.length} aluno(s) na turma
        </p>

        {error && <div className={s.error}>{error}</div>}

        {loadingAlunos ? (
          <p className={s.muted}>A carregar alunos...</p>
        ) : notaRows.length === 0 ? (
          <p className={s.muted}>Esta turma não tem alunos alocados.</p>
        ) : (
          <form onSubmit={handleSubmitNotas}>
            <div className={s.table}>
              <table>
                <thead>
                  <tr>
                    <th>Aluno</th>
                    <th>Nº Processo</th>
                    <th style={{ width: 120 }}>Nota</th>
                    <th>Observações</th>
                  </tr>
                </thead>
                <tbody>
                  {notaRows.map((row, idx) => (
                    <tr key={row.aluno_id}>
                      <td>{row.nome}</td>
                      <td>{row.n_processo}</td>
                      <td>
                        <input
                          className={s.input}
                          type="number"
                          step="0.1"
                          min="0"
                          max={selectedAval.nota_maxima}
                          placeholder="—"
                          value={row.valor}
                          onChange={(e) => updateNotaRow(idx, "valor", e.target.value)}
                          style={{ width: "100%" }}
                        />
                      </td>
                      <td>
                        <input
                          className={s.input}
                          placeholder="(opcional)"
                          value={row.observacoes}
                          onChange={(e) =>
                            updateNotaRow(idx, "observacoes", e.target.value)
                          }
                          style={{ width: "100%" }}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className={s.formActions} style={{ marginTop: 16 }}>
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
        )}
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

      {/* Selectors — turmas e disciplinas do professor logado */}
      <div className={s.section}>
        <div className={s.formGrid} style={{ maxWidth: 600 }}>
          <div className={s.field}>
            <label className={s.label}>Turma</label>
            <select
              className={s.input}
              value={selectedTurmaId}
              onChange={(e) => setSelectedTurmaId(e.target.value)}
              disabled={!professorId || turmas.length === 0}
            >
              <option value="">
                {!professorId
                  ? "Utilizador sem perfil de professor"
                  : turmas.length === 0
                    ? "Sem turmas atribuídas"
                    : "-- Seleccionar turma --"}
              </option>
              {turmas.map((t) => (
                <option key={t.turma_id} value={t.turma_id}>
                  {t.nome} ({t.classe}) {t.is_regente ? "★ regente" : ""}
                </option>
              ))}
            </select>
          </div>
          <div className={s.field}>
            <label className={s.label}>Disciplina (opcional)</label>
            <select
              className={s.input}
              value={disciplinaId}
              onChange={(e) => setDisciplinaId(e.target.value)}
              disabled={!selectedTurmaId || disciplinas.length === 0}
            >
              <option value="">
                {!selectedTurmaId ? "Seleccione primeiro a turma" : "Todas as disciplinas"}
              </option>
              {disciplinas.map((d) => (
                <option key={d.disciplina_id} value={d.disciplina_id}>
                  {d.nome} ({d.codigo})
                </option>
              ))}
            </select>
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
