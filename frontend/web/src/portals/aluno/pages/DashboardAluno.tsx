import { useEffect, useState } from "react";
import { BookOpen, XCircle, AlertTriangle } from "lucide-react";
import api from "@/shared/api/client";
import type { NotaResponse, FaltaResumoResponse } from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

export default function DashboardAluno() {
  const { user } = useAuth();
  const [notas, setNotas] = useState<NotaResponse[]>([]);
  const [faltasResumo, setFaltasResumo] = useState<FaltaResumoResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!user?.id) return;

    Promise.all([
      api.get<NotaResponse[]>(`/alunos/${user.id}/notas?periodo=1`).catch(() => null),
      api.get<FaltaResumoResponse>(`/alunos/${user.id}/faltas/resumo`).catch(() => null),
    ])
      .then(([notasRes, faltasRes]) => {
        if (notasRes) setNotas(notasRes.data);
        if (faltasRes) setFaltasResumo(faltasRes.data);
        if (!notasRes && !faltasRes) setError(true);
      })
      .finally(() => setLoading(false));
  }, [user?.id]);

  const cards = [
    {
      label: "Total Notas",
      value: error ? "--" : notas.length,
      icon: BookOpen,
      color: "#1A3F7A",
    },
    {
      label: "Faltas Total",
      value: error ? "--" : (faltasResumo?.total ?? 0),
      icon: XCircle,
      color: "#DD6B20",
    },
    {
      label: "Faltas Injustificadas",
      value: error ? "--" : (faltasResumo?.injustificadas ?? 0),
      icon: AlertTriangle,
      color: "#E53E3E",
    },
  ];

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>
            Bem-vindo{user?.nome_completo ? `, ${user.nome_completo}` : ""}
          </h1>
          <p className={s.subtitle}>Painel do Aluno</p>
        </div>
      </div>

      {loading ? (
        <p className={s.muted}>A carregar...</p>
      ) : error ? (
        <div className={s.emptyState}>
          <div className={s.emptyIcon}>
            <AlertTriangle size={48} />
          </div>
          <p>Dados nao disponiveis. O seu perfil de aluno podera ainda nao estar associado.</p>
        </div>
      ) : (
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
      )}
    </div>
  );
}
