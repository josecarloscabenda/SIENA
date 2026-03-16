import { useEffect, useState } from "react";
import { XCircle, CheckCircle, AlertTriangle } from "lucide-react";
import api from "@/shared/api/client";
import type { FaltaResponse, FaltaResumoResponse } from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

type FiltroTipo = "all" | "justificada" | "injustificada";

export default function MinhasFaltas() {
  const { user } = useAuth();
  const [faltas, setFaltas] = useState<FaltaResponse[]>([]);
  const [resumo, setResumo] = useState<FaltaResumoResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filtro, setFiltro] = useState<FiltroTipo>("all");

  useEffect(() => {
    if (!user?.id) return;

    setLoading(true);
    setError("");

    Promise.all([
      api.get<FaltaResponse[]>(`/alunos/${user.id}/faltas`),
      api.get<FaltaResumoResponse>(`/alunos/${user.id}/faltas/resumo`),
    ])
      .then(([faltasRes, resumoRes]) => {
        setFaltas(faltasRes.data);
        setResumo(resumoRes.data);
      })
      .catch(() => {
        setError("Nao foi possivel carregar as faltas. O seu perfil podera ainda nao estar associado.");
      })
      .finally(() => setLoading(false));
  }, [user?.id]);

  const filteredFaltas =
    filtro === "all"
      ? faltas
      : faltas.filter((f) => f.tipo === filtro);

  const statCards = [
    {
      label: "Total",
      value: resumo?.total ?? 0,
      icon: XCircle,
      color: "#1A3F7A",
    },
    {
      label: "Justificadas",
      value: resumo?.justificadas ?? 0,
      icon: CheckCircle,
      color: "#00A878",
    },
    {
      label: "Injustificadas",
      value: resumo?.injustificadas ?? 0,
      icon: AlertTriangle,
      color: "#E53E3E",
    },
  ];

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>Minhas Faltas</h1>
          <p className={s.subtitle}>Consulte o registo das suas faltas</p>
        </div>
      </div>

      {loading ? (
        <p className={s.muted}>A carregar...</p>
      ) : error ? (
        <div className={s.emptyState}>
          <div className={s.emptyIcon}>
            <AlertTriangle size={48} />
          </div>
          <p>{error}</p>
        </div>
      ) : (
        <>
          {/* Summary cards */}
          <div className={s.statsGrid}>
            {statCards.map((card) => {
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

          {/* Filter tabs */}
          <div className={s.tabs}>
            {([
              { key: "all" as FiltroTipo, label: "Todas" },
              { key: "justificada" as FiltroTipo, label: "Justificadas" },
              { key: "injustificada" as FiltroTipo, label: "Injustificadas" },
            ]).map((item) => (
              <button
                key={item.key}
                className={`${s.tab} ${filtro === item.key ? s.tabActive : ""}`}
                onClick={() => setFiltro(item.key)}
              >
                {item.label}
              </button>
            ))}
          </div>

          {/* Faltas table */}
          {filteredFaltas.length === 0 ? (
            <div className={s.emptyState}>
              <p>Sem faltas registadas{filtro !== "all" ? ` do tipo "${filtro}"` : ""}.</p>
            </div>
          ) : (
            <div className={s.table}>
              <table>
                <thead>
                  <tr>
                    <th>Data</th>
                    <th>Disciplina ID</th>
                    <th>Tipo</th>
                    <th>Justificativa</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredFaltas.map((falta) => (
                    <tr key={falta.id}>
                      <td>{new Date(falta.data).toLocaleDateString("pt-AO")}</td>
                      <td title={falta.disciplina_id}>
                        {falta.disciplina_id.slice(0, 8)}...
                      </td>
                      <td>
                        <span
                          className={`${s.badge} ${
                            falta.tipo === "justificada"
                              ? s.badgeGreen
                              : s.badgeRed
                          }`}
                        >
                          {falta.tipo}
                        </span>
                      </td>
                      <td>{falta.justificativa ?? "--"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}
