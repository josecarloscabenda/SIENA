import { useEffect, useState } from "react";
import { ClipboardList } from "lucide-react";
import api from "@/shared/api/client";
import type {
  TurmaResponse,
  DisciplinaResponse,
  AvaliacaoResponse,
  NotaResponse,
  PaginatedResponse,
} from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

interface StudentRow {
  aluno_id: string;
  notas: Record<string, number | null>; /* avaliacao_id → valor */
}

export default function Pauta() {
  useAuth(); // ensure authenticated
  const [turmas, setTurmas] = useState<TurmaResponse[]>([]);
  const [disciplinas, setDisciplinas] = useState<DisciplinaResponse[]>([]);
  const [selectedTurma, setSelectedTurma] = useState("");
  const [selectedDisciplina, setSelectedDisciplina] = useState("");
  const [periodo, setPeriodo] = useState<number>(1);

  const [avaliacoes, setAvaliacoes] = useState<AvaliacaoResponse[]>([]);
  const [students, setStudents] = useState<StudentRow[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api
      .get<PaginatedResponse<TurmaResponse>>("/turmas?limit=100")
      .then(({ data }) => setTurmas(data.items))
      .catch(() => {});
    api
      .get<PaginatedResponse<DisciplinaResponse>>("/disciplinas?limit=100")
      .then(({ data }) => setDisciplinas(data.items))
      .catch(() => {});
  }, []);

  /* Fetch avaliacoes when filters change */
  useEffect(() => {
    if (!selectedTurma || !selectedDisciplina) {
      setAvaliacoes([]);
      setStudents([]);
      return;
    }
    setLoading(true);
    api
      .get<PaginatedResponse<AvaliacaoResponse>>(
        `/avaliacoes?turma_id=${selectedTurma}&disciplina_id=${selectedDisciplina}`,
      )
      .then(({ data }) => {
        const filtered = data.items.filter((a) => a.periodo === periodo);
        setAvaliacoes(filtered);
        return filtered;
      })
      .then(async (avs) => {
        if (avs.length === 0) {
          setStudents([]);
          return;
        }
        /* Fetch notas for each avaliacao */
        const allNotas: NotaResponse[] = [];
        for (const av of avs) {
          try {
            const { data } = await api.get<NotaResponse[]>(`/avaliacoes/${av.id}/notas`);
            allNotas.push(...data);
          } catch {
            /* skip */
          }
        }
        /* Build student rows */
        const map = new Map<string, Record<string, number | null>>();
        for (const nota of allNotas) {
          if (!map.has(nota.aluno_id)) map.set(nota.aluno_id, {});
          map.get(nota.aluno_id)![nota.avaliacao_id] = nota.valor;
        }
        const rows: StudentRow[] = Array.from(map.entries()).map(([aluno_id, notas]) => ({
          aluno_id,
          notas,
        }));
        setStudents(rows);
      })
      .catch(() => {
        setAvaliacoes([]);
        setStudents([]);
      })
      .finally(() => setLoading(false));
  }, [selectedTurma, selectedDisciplina, periodo]);

  const formatDate = (iso: string) => {
    const d = new Date(iso);
    return `${String(d.getDate()).padStart(2, "0")}/${String(d.getMonth() + 1).padStart(2, "0")}`;
  };

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>Pauta de Avaliações</h1>
          <p className={s.subtitle}>Visualização da pauta por turma e disciplina</p>
        </div>
      </div>

      {/* Filters */}
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 20 }}>
        <div className={s.field}>
          <label className={s.label}>Turma</label>
          <select
            className={s.input}
            style={{ minWidth: 220 }}
            value={selectedTurma}
            onChange={(e) => setSelectedTurma(e.target.value)}
          >
            <option value="">Selecionar turma...</option>
            {turmas.map((t) => (
              <option key={t.id} value={t.id}>
                {t.nome} - Classe {t.classe}
              </option>
            ))}
          </select>
        </div>

        <div className={s.field}>
          <label className={s.label}>Disciplina</label>
          <select
            className={s.input}
            style={{ minWidth: 220 }}
            value={selectedDisciplina}
            onChange={(e) => setSelectedDisciplina(e.target.value)}
          >
            <option value="">Selecionar disciplina...</option>
            {disciplinas.map((d) => (
              <option key={d.id} value={d.id}>
                {d.nome} ({d.codigo})
              </option>
            ))}
          </select>
        </div>

        <div className={s.field}>
          <label className={s.label}>Período</label>
          <select
            className={s.input}
            value={periodo}
            onChange={(e) => setPeriodo(Number(e.target.value))}
          >
            <option value={1}>1.º Período</option>
            <option value={2}>2.º Período</option>
            <option value={3}>3.º Período</option>
          </select>
        </div>
      </div>

      {/* Content */}
      {!selectedTurma || !selectedDisciplina ? (
        <div className={s.emptyState}>
          <div className={s.emptyIcon}><ClipboardList size={48} /></div>
          <p>Selecione uma turma e uma disciplina para visualizar a pauta.</p>
        </div>
      ) : loading ? (
        <p className={s.muted}>A carregar...</p>
      ) : avaliacoes.length === 0 ? (
        <p className={s.muted}>Nenhuma avaliação encontrada para o período seleccionado.</p>
      ) : (
        <div className={s.table}>
          <table>
            <thead>
              <tr>
                <th>Aluno ID</th>
                {avaliacoes.map((av) => (
                  <th key={av.id} style={{ textAlign: "center" }}>
                    {av.tipo}
                    <br />
                    <span style={{ fontWeight: 400, fontSize: "0.7rem" }}>
                      {formatDate(av.data)}
                    </span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {students.length === 0 ? (
                <tr>
                  <td colSpan={avaliacoes.length + 1}>
                    <p className={s.muted} style={{ textAlign: "center" }}>
                      Nenhuma nota registada.
                    </p>
                  </td>
                </tr>
              ) : (
                students.map((st) => (
                  <tr key={st.aluno_id}>
                    <td style={{ fontFamily: "monospace", fontSize: "0.75rem" }}>
                      {st.aluno_id.substring(0, 8)}...
                    </td>
                    {avaliacoes.map((av) => (
                      <td key={av.id} style={{ textAlign: "center" }}>
                        {st.notas[av.id] != null ? (
                          <span className={`${s.badge} ${s.badgeBlue}`}>
                            {st.notas[av.id]}
                          </span>
                        ) : (
                          <span className={s.muted}>—</span>
                        )}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
