import { useEffect, useState } from "react";
import {
  BookOpen,
  XCircle,
  AlertTriangle,
  Award,
  Calendar,
  Hash,
  LayoutGrid,
  CheckCircle,
} from "lucide-react";
import api from "@/shared/api/client";
import type { AlunoStats } from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

const tipoLabel: Record<string, string> = {
  teste: "Teste",
  trabalho: "Trabalho",
  exame: "Exame",
  oral: "Oral",
};

export default function DashboardAluno() {
  const { user } = useAuth();
  const [stats, setStats] = useState<AlunoStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user?.aluno_id) {
      setLoading(false);
      setError("O seu perfil de aluno ainda não está associado.");
      return;
    }
    api
      .get<AlunoStats>("/dashboard/aluno")
      .then(({ data }) => setStats(data))
      .catch(() => setError("Não foi possível carregar o painel."))
      .finally(() => setLoading(false));
  }, [user?.aluno_id]);

  if (loading) return <p className={s.muted}>A carregar...</p>;

  if (error || !stats) {
    return (
      <div>
        <h1 className={s.pageTitle}>Painel do Aluno</h1>
        <div className={s.emptyState}>
          <div className={s.emptyIcon}>
            <AlertTriangle size={48} />
          </div>
          <p>{error ?? "Sem dados."}</p>
        </div>
      </div>
    );
  }

  const cards = [
    {
      label: "Média Geral",
      value: stats.media_geral ? Number(stats.media_geral).toFixed(2) : "—",
      icon: Award,
      color: "#1A3F7A",
    },
    { label: "Faltas Total", value: stats.total_faltas, icon: XCircle, color: "#DD6B20" },
    {
      label: "Faltas Injustificadas",
      value: stats.faltas_injustificadas,
      icon: AlertTriangle,
      color: "#E53E3E",
    },
    {
      label: "Próximas Avaliações",
      value: stats.proximas_avaliacoes.length,
      icon: Calendar,
      color: "#00A878",
    },
  ];

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>
            Olá{stats.nome ? `, ${stats.nome}` : ""}
          </h1>
          <p className={s.subtitle}>
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
        </div>
      </div>

      <div className={s.statsGrid}>
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.label} className={s.statCard}>
              <div
                className={s.statIcon}
                style={{ background: `${card.color}20`, color: card.color }}
              >
                <Icon size={24} />
              </div>
              <div>
                <div className={s.statValue}>{card.value}</div>
                <div className={s.statLabel}>{card.label}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Médias por disciplina */}
      <div className={s.section} style={{ marginTop: 24 }}>
        <h2 className={s.sectionTitle}>
          <BookOpen size={18} style={{ marginRight: 8, verticalAlign: "middle" }} />
          Resumo por Disciplina
        </h2>
        {stats.disciplinas.length === 0 ? (
          <p className={s.muted}>Sem notas ou faltas registadas.</p>
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
                {stats.disciplinas.map((d) => {
                  const m = d.media ? Number(d.media) : null;
                  const cor =
                    m === null ? "" : m >= 10 ? s.badgeGreen : s.badgeRed;
                  return (
                    <tr key={d.disciplina_id}>
                      <td>{d.disciplina_nome}</td>
                      <td>
                        {m === null ? (
                          <span className={s.muted}>—</span>
                        ) : (
                          <span className={`${s.badge} ${cor}`}>{m.toFixed(2)}</span>
                        )}
                      </td>
                      <td>
                        {d.faltas === 0 ? (
                          <CheckCircle size={14} color="#38A169" />
                        ) : (
                          d.faltas
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Próximas avaliações */}
      <div className={s.section} style={{ marginTop: 24 }}>
        <h2 className={s.sectionTitle}>
          <Calendar size={18} style={{ marginRight: 8, verticalAlign: "middle" }} />
          Próximas Avaliações
        </h2>
        {stats.proximas_avaliacoes.length === 0 ? (
          <p className={s.muted}>Sem avaliações agendadas.</p>
        ) : (
          <div className={s.table}>
            <table>
              <thead>
                <tr>
                  <th>Data</th>
                  <th>Disciplina</th>
                  <th>Tipo</th>
                  <th>Nota Máxima</th>
                </tr>
              </thead>
              <tbody>
                {stats.proximas_avaliacoes.map((av) => (
                  <tr key={av.avaliacao_id}>
                    <td>{new Date(av.data).toLocaleDateString("pt-AO")}</td>
                    <td>{av.disciplina_nome}</td>
                    <td>
                      <span className={`${s.badge} ${s.badgeBlue}`}>
                        {tipoLabel[av.tipo] || av.tipo}
                      </span>
                    </td>
                    <td>{av.nota_maxima}</td>
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
