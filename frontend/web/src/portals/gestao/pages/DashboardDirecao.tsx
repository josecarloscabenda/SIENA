import { useEffect, useState } from "react";
import {
  Users,
  Users2,
  LayoutGrid,
  FileText,
  BookOpen,
  UserCheck,
  ClipboardCheck,
  AlertCircle,
} from "lucide-react";
import api from "@/shared/api/client";
import type { GestaoStats } from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

export default function DashboardDirecao() {
  const { user } = useAuth();
  const [stats, setStats] = useState<GestaoStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<GestaoStats>("/dashboard/gestao")
      .then(({ data }) => setStats(data))
      .catch(() => setStats(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div>
        <h1 className={s.pageTitle}>Painel de Direcção / Secretaria</h1>
        <p className={s.muted}>A carregar...</p>
      </div>
    );
  }

  if (!stats) {
    return (
      <div>
        <h1 className={s.pageTitle}>Painel de Direcção / Secretaria</h1>
        <p className={s.muted}>Não foi possível carregar as estatísticas.</p>
      </div>
    );
  }

  const cards = [
    { label: "Total Alunos", value: stats.total_alunos, icon: Users, color: "#1A3F7A" },
    { label: "Alunos Activos", value: stats.total_alunos_ativos, icon: UserCheck, color: "#00A878" },
    { label: "Professores", value: stats.total_professores, icon: Users2, color: "#805AD5" },
    { label: "Encarregados", value: stats.total_encarregados, icon: UserCheck, color: "#3182CE" },
    { label: "Turmas", value: stats.total_turmas, icon: LayoutGrid, color: "#319795" },
    { label: "Disciplinas", value: stats.total_disciplinas, icon: BookOpen, color: "#D69E2E" },
    { label: "Avaliações Lançadas", value: stats.avaliacoes_total, icon: ClipboardCheck, color: "#38A169" },
    { label: "Matrículas Pendentes", value: stats.matriculas_pendentes, icon: AlertCircle, color: "#DD6B20" },
  ];

  const total =
    stats.matriculas_pendentes + stats.matriculas_aprovadas + stats.matriculas_rejeitadas;
  const pct = (n: number) => (total === 0 ? 0 : (n / total) * 100);

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>
            Bem-vindo{user?.nome_completo ? `, ${user.nome_completo}` : ""}
          </h1>
          <p className={s.subtitle}>Painel de Direcção / Secretaria</p>
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

      {/* Gráfico de matrículas por estado (#45) */}
      <div className={s.section} style={{ marginTop: 24 }}>
        <h2 className={s.sectionTitle}>
          <FileText size={18} style={{ marginRight: 8, verticalAlign: "middle" }} />
          Matrículas por Estado
        </h2>
        <p className={s.muted} style={{ fontSize: "0.85rem", marginBottom: 12 }}>
          Distribuição de {total} matrícula(s) registada(s) na escola.
        </p>

        {total === 0 ? (
          <p className={s.muted}>Sem matrículas registadas.</p>
        ) : (
          <>
            <div
              style={{
                display: "flex",
                width: "100%",
                height: 28,
                borderRadius: 6,
                overflow: "hidden",
                border: "1px solid #e5e7eb",
                marginBottom: 12,
              }}
              title={`Pendentes: ${stats.matriculas_pendentes} · Aprovadas: ${stats.matriculas_aprovadas} · Rejeitadas: ${stats.matriculas_rejeitadas}`}
            >
              {stats.matriculas_aprovadas > 0 && (
                <div
                  style={{
                    background: "#38A169",
                    width: `${pct(stats.matriculas_aprovadas)}%`,
                  }}
                />
              )}
              {stats.matriculas_pendentes > 0 && (
                <div
                  style={{
                    background: "#DD6B20",
                    width: `${pct(stats.matriculas_pendentes)}%`,
                  }}
                />
              )}
              {stats.matriculas_rejeitadas > 0 && (
                <div
                  style={{
                    background: "#E53E3E",
                    width: `${pct(stats.matriculas_rejeitadas)}%`,
                  }}
                />
              )}
            </div>

            <div style={{ display: "flex", gap: 16, fontSize: "0.85rem", flexWrap: "wrap" }}>
              <span>
                <span
                  style={{
                    display: "inline-block",
                    width: 12,
                    height: 12,
                    background: "#38A169",
                    borderRadius: 2,
                    marginRight: 6,
                    verticalAlign: "middle",
                  }}
                />
                Aprovadas: <strong>{stats.matriculas_aprovadas}</strong>
                <span className={s.muted}> ({pct(stats.matriculas_aprovadas).toFixed(1)}%)</span>
              </span>
              <span>
                <span
                  style={{
                    display: "inline-block",
                    width: 12,
                    height: 12,
                    background: "#DD6B20",
                    borderRadius: 2,
                    marginRight: 6,
                    verticalAlign: "middle",
                  }}
                />
                Pendentes: <strong>{stats.matriculas_pendentes}</strong>
                <span className={s.muted}> ({pct(stats.matriculas_pendentes).toFixed(1)}%)</span>
              </span>
              <span>
                <span
                  style={{
                    display: "inline-block",
                    width: 12,
                    height: 12,
                    background: "#E53E3E",
                    borderRadius: 2,
                    marginRight: 6,
                    verticalAlign: "middle",
                  }}
                />
                Rejeitadas: <strong>{stats.matriculas_rejeitadas}</strong>
                <span className={s.muted}> ({pct(stats.matriculas_rejeitadas).toFixed(1)}%)</span>
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
