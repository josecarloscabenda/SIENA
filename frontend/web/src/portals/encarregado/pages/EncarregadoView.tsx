import { useEffect, useMemo, useState } from "react";
import {
  Users,
  AlertTriangle,
  Award,
  XCircle,
  CheckCircle,
  Hash,
  LayoutGrid,
} from "lucide-react";
import api from "@/shared/api/client";
import type {
  AlunoStats,
  BoletimResponse,
  EncarregadoStats,
  FaltaResponse,
} from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

type Tab = "resumo" | "boletim" | "faltas";

export default function EncarregadoView() {
  const { user } = useAuth();
  const [stats, setStats] = useState<EncarregadoStats | null>(null);
  const [loadingStats, setLoadingStats] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedAlunoId, setSelectedAlunoId] = useState<string>("");
  const [tab, setTab] = useState<Tab>("resumo");

  /* Per-aluno data */
  const [alunoStats, setAlunoStats] = useState<AlunoStats | null>(null);
  const [loadingAluno, setLoadingAluno] = useState(false);
  const [boletim, setBoletim] = useState<BoletimResponse | null>(null);
  const [faltas, setFaltas] = useState<FaltaResponse[]>([]);
  const [periodo, setPeriodo] = useState(1);

  /* Load encarregado dashboard once */
  useEffect(() => {
    if (!user?.encarregado_id) {
      setLoadingStats(false);
      setError("O seu perfil de encarregado ainda não está associado.");
      return;
    }
    api
      .get<EncarregadoStats>("/dashboard/encarregado")
      .then(({ data }) => {
        setStats(data);
        if (data.educandos.length > 0) {
          setSelectedAlunoId(data.educandos[0].aluno_id);
        }
      })
      .catch(() => setError("Não foi possível carregar os dados."))
      .finally(() => setLoadingStats(false));
  }, [user?.encarregado_id]);

  /* Load selected aluno detail */
  useEffect(() => {
    if (!selectedAlunoId) {
      setAlunoStats(null);
      return;
    }
    setLoadingAluno(true);
    api
      .get<AlunoStats>(`/dashboard/aluno?aluno_id=${selectedAlunoId}`)
      .then(({ data }) => setAlunoStats(data))
      .catch(() => setAlunoStats(null))
      .finally(() => setLoadingAluno(false));
  }, [selectedAlunoId]);

  /* Load boletim when tab=boletim */
  useEffect(() => {
    if (tab !== "boletim" || !selectedAlunoId) return;
    api
      .get<BoletimResponse>(
        `/alunos/${selectedAlunoId}/boletim?periodo=${periodo}`,
      )
      .then(({ data }) => setBoletim(data))
      .catch(() => setBoletim(null));
  }, [tab, selectedAlunoId, periodo]);

  /* Load faltas list when tab=faltas */
  useEffect(() => {
    if (tab !== "faltas" || !selectedAlunoId) return;
    api
      .get<FaltaResponse[]>(`/alunos/${selectedAlunoId}/faltas`)
      .then(({ data }) => setFaltas(data))
      .catch(() => setFaltas([]));
  }, [tab, selectedAlunoId]);

  const selectedEducando = useMemo(
    () => stats?.educandos.find((e) => e.aluno_id === selectedAlunoId),
    [stats, selectedAlunoId],
  );

  if (loadingStats) return <p className={s.muted}>A carregar...</p>;

  if (error || !stats) {
    return (
      <div>
        <h1 className={s.pageTitle}>Portal do Encarregado</h1>
        <div className={s.emptyState}>
          <div className={s.emptyIcon}>
            <AlertTriangle size={48} />
          </div>
          <p>{error ?? "Sem dados."}</p>
        </div>
      </div>
    );
  }

  if (stats.educandos.length === 0) {
    return (
      <div>
        <h1 className={s.pageTitle}>Olá, {stats.nome}</h1>
        <p className={s.subtitle}>Portal do Encarregado</p>
        <div className={s.emptyState}>
          <div className={s.emptyIcon}>
            <Users size={48} />
          </div>
          <p>Não há educandos vinculados ao seu perfil.</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>Olá, {stats.nome}</h1>
          <p className={s.subtitle}>
            Portal do Encarregado · {stats.educandos.length} educando(s)
          </p>
        </div>
      </div>

      {/* Lista de educandos como cards selectáveis (#48) */}
      <div className={s.statsGrid} style={{ marginBottom: 16 }}>
        {stats.educandos.map((e) => {
          const active = e.aluno_id === selectedAlunoId;
          return (
            <button
              key={e.aluno_id}
              type="button"
              onClick={() => {
                setSelectedAlunoId(e.aluno_id);
                setTab("resumo");
              }}
              className={s.statCard}
              style={{
                cursor: "pointer",
                textAlign: "left",
                border: active ? "2px solid #1A3F7A" : "1px solid #e5e7eb",
                background: active ? "#F0F4FA" : "#fff",
              }}
            >
              <div
                className={s.statIcon}
                style={{ background: "#1A3F7A20", color: "#1A3F7A" }}
              >
                <Users size={24} />
              </div>
              <div>
                <div className={s.statValue} style={{ fontSize: "1rem" }}>
                  {e.nome}
                </div>
                <div className={s.statLabel}>
                  {e.classe ? `${e.classe} · ` : ""}
                  {e.turma_nome ?? "sem turma"}
                  {" · média "}
                  {e.media_geral ? Number(e.media_geral).toFixed(1) : "—"}
                  {" · faltas "}
                  {e.total_faltas}
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {selectedEducando && (
        <>
          <div className={s.tabs}>
            {(["resumo", "boletim", "faltas"] as Tab[]).map((t) => (
              <button
                key={t}
                className={`${s.tab} ${tab === t ? s.tabActive : ""}`}
                onClick={() => setTab(t)}
              >
                {t === "resumo" ? "Resumo" : t === "boletim" ? "Boletim" : "Faltas"}
              </button>
            ))}
          </div>

          {tab === "resumo" && (
            <ResumoTab loading={loadingAluno} stats={alunoStats} />
          )}

          {tab === "boletim" && (
            <BoletimTab
              boletim={boletim}
              periodo={periodo}
              setPeriodo={setPeriodo}
            />
          )}

          {tab === "faltas" && <FaltasTab faltas={faltas} />}
        </>
      )}
    </div>
  );
}

/* ── Subcomponentes ─────────────────────────── */

function ResumoTab({ loading, stats }: { loading: boolean; stats: AlunoStats | null }) {
  if (loading) return <p className={s.muted}>A carregar...</p>;
  if (!stats) return <p className={s.muted}>Sem dados.</p>;
  const cards = [
    {
      label: "Média Geral",
      value: stats.media_geral ? Number(stats.media_geral).toFixed(2) : "—",
      icon: Award,
      color: "#1A3F7A",
    },
    { label: "Total Faltas", value: stats.total_faltas, icon: XCircle, color: "#DD6B20" },
    {
      label: "Faltas Injustificadas",
      value: stats.faltas_injustificadas,
      icon: AlertTriangle,
      color: "#E53E3E",
    },
    {
      label: "Próximas Avaliações",
      value: stats.proximas_avaliacoes.length,
      icon: CheckCircle,
      color: "#00A878",
    },
  ];
  return (
    <>
      <p className={s.subtitle} style={{ margin: "16px 0" }}>
        <Hash size={14} style={{ verticalAlign: "middle", marginRight: 4 }} />
        Nº processo {stats.n_processo}
        {stats.classe && (
          <>
            {" · "}
            <LayoutGrid size={14} style={{ verticalAlign: "middle", marginRight: 4 }} />
            {stats.classe} {stats.turma_nome ? `(${stats.turma_nome})` : ""}
          </>
        )}
      </p>
      <div className={s.statsGrid}>
        {cards.map((c) => {
          const Icon = c.icon;
          return (
            <div key={c.label} className={s.statCard}>
              <div
                className={s.statIcon}
                style={{ background: `${c.color}20`, color: c.color }}
              >
                <Icon size={24} />
              </div>
              <div>
                <div className={s.statValue}>{c.value}</div>
                <div className={s.statLabel}>{c.label}</div>
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
}

function BoletimTab({
  boletim,
  periodo,
  setPeriodo,
}: {
  boletim: BoletimResponse | null;
  periodo: number;
  setPeriodo: (p: number) => void;
}) {
  return (
    <div>
      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        {[1, 2, 3].map((p) => (
          <button
            key={p}
            className={`${s.tab} ${periodo === p ? s.tabActive : ""}`}
            onClick={() => setPeriodo(p)}
          >
            {p}.º Período
          </button>
        ))}
      </div>
      {!boletim || boletim.disciplinas.length === 0 ? (
        <p className={s.muted}>Sem dados de boletim para este período.</p>
      ) : (
        <div className={s.table}>
          <table>
            <thead>
              <tr>
                <th>Disciplina</th>
                <th>Média</th>
                <th>Faltas</th>
              </tr>
            </thead>
            <tbody>
              {boletim.disciplinas.map((disc) => (
                <tr key={disc.disciplina_id}>
                  <td>{disc.disciplina_nome}</td>
                  <td>
                    {disc.media !== null ? (
                      <span
                        className={`${s.badge} ${
                          Number(disc.media) >= 10 ? s.badgeGreen : s.badgeRed
                        }`}
                      >
                        {Number(disc.media).toFixed(1)}
                      </span>
                    ) : (
                      <span className={`${s.badge} ${s.badgeGray}`}>—</span>
                    )}
                  </td>
                  <td>{disc.faltas_total}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function FaltasTab({ faltas }: { faltas: FaltaResponse[] }) {
  if (faltas.length === 0) {
    return <p className={s.muted}>Sem faltas registadas.</p>;
  }
  return (
    <div className={s.table}>
      <table>
        <thead>
          <tr>
            <th>Data</th>
            <th>Disciplina</th>
            <th>Tipo</th>
            <th>Justificação</th>
          </tr>
        </thead>
        <tbody>
          {faltas.map((f) => (
            <tr key={f.id}>
              <td>{new Date(f.data).toLocaleDateString("pt-AO")}</td>
              <td>{f.disciplina_nome ?? "—"}</td>
              <td>
                <span
                  className={`${s.badge} ${
                    f.tipo === "justificada" ? s.badgeGreen : s.badgeRed
                  }`}
                >
                  {f.tipo === "justificada" ? "Justificada" : "Injustificada"}
                </span>
              </td>
              <td>{f.justificativa || <span className={s.muted}>—</span>}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
