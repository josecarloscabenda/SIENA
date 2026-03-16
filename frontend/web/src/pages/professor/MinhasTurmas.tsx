import { useEffect, useState } from "react";
import { Search, LayoutGrid, ArrowLeft } from "lucide-react";
import api from "@/shared/api/client";
import type {
  TurmaResponse,
  TurmaDetailResponse,
  HorarioAulaResponse,
  PaginatedResponse,
} from "@/shared/api/types";
import s from "@/shared/styles/common.module.css";

const turnoLabel: Record<string, string> = {
  matutino: "Matutino",
  vespertino: "Vespertino",
  nocturno: "Nocturno",
};

export default function MinhasTurmas() {
  const [turmas, setTurmas] = useState<TurmaResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  // Detail view
  const [selectedTurma, setSelectedTurma] = useState<TurmaResponse | null>(null);
  const [horarios, setHorarios] = useState<HorarioAulaResponse[]>([]);
  const [loadingDetail, setLoadingDetail] = useState(false);

  useEffect(() => {
    api
      .get<PaginatedResponse<TurmaResponse>>("/turmas?limit=100")
      .then(({ data }) => setTurmas(data.items))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = turmas.filter((t) => {
    const q = search.toLowerCase();
    return (
      t.nome.toLowerCase().includes(q) ||
      t.classe.toLowerCase().includes(q) ||
      (t.sala?.toLowerCase().includes(q) ?? false)
    );
  });

  const openDetail = (turma: TurmaResponse) => {
    setSelectedTurma(turma);
    setLoadingDetail(true);
    api
      .get<TurmaDetailResponse>(`/turmas/${turma.id}`)
      .then(({ data }) => setHorarios(data.horarios))
      .catch(() => setHorarios([]))
      .finally(() => setLoadingDetail(false));
  };

  if (selectedTurma) {
    return (
      <div>
        <button className={s.backBtn} onClick={() => setSelectedTurma(null)}>
          <ArrowLeft size={16} /> Voltar
        </button>

        <div className={s.pageHeader}>
          <div>
            <h1 className={s.pageTitle}>{selectedTurma.nome}</h1>
            <p className={s.subtitle}>
              {selectedTurma.classe} &middot;{" "}
              {turnoLabel[selectedTurma.turno] || selectedTurma.turno}
              {selectedTurma.sala ? ` · Sala ${selectedTurma.sala}` : ""}
            </p>
          </div>
        </div>

        <div className={s.section}>
          <h2 className={s.sectionTitle}>Horários</h2>
          {loadingDetail ? (
            <p className={s.muted}>A carregar...</p>
          ) : horarios.length === 0 ? (
            <p className={s.muted}>Nenhum horário registado para esta turma.</p>
          ) : (
            <div className={s.table}>
              <table>
                <thead>
                  <tr>
                    <th>Dia</th>
                    <th>Hora Início</th>
                    <th>Hora Fim</th>
                    <th>Disciplina ID</th>
                  </tr>
                </thead>
                <tbody>
                  {horarios.map((h) => (
                    <tr key={h.id}>
                      <td>{h.dia_semana}</td>
                      <td>{h.hora_inicio}</td>
                      <td>{h.hora_fim}</td>
                      <td style={{ fontFamily: "monospace", fontSize: "0.8rem" }}>
                        {h.disciplina_id}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>Minhas Turmas</h1>
          <p className={s.subtitle}>{turmas.length} turma(s)</p>
        </div>
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
                <th>Acções</th>
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
                  <td>
                    <button
                      className={s.editBtn}
                      onClick={() => openDetail(turma)}
                    >
                      Ver Horários
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
