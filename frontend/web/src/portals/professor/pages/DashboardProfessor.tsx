import { useEffect, useState } from "react";
import { LayoutGrid, CalendarDays } from "lucide-react";
import api from "@/shared/api/client";
import type { TurmaResponse, PaginatedResponse } from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

const turnoLabel: Record<string, string> = {
  matutino: "Matutino",
  vespertino: "Vespertino",
  nocturno: "Nocturno",
};

export default function DashboardProfessor() {
  const { user } = useAuth();
  const [turmas, setTurmas] = useState<TurmaResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<PaginatedResponse<TurmaResponse>>("/turmas?limit=100")
      .then(({ data }) => {
        const minhas = data.items.filter(
          (t) => t.professor_regente_id === user?.id,
        );
        setTurmas(minhas);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [user?.id]);

  const cards = [
    {
      label: "Minhas Turmas",
      value: turmas.length,
      icon: LayoutGrid,
      color: "#1A3F7A",
    },
    {
      label: "Próximas Aulas",
      value: 0,
      icon: CalendarDays,
      color: "#00A878",
    },
  ];

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>
            Bem-vindo{user?.nome_completo ? `, ${user.nome_completo}` : ""}
          </h1>
          <p className={s.subtitle}>Painel do Professor</p>
        </div>
      </div>

      {loading ? (
        <p className={s.muted}>A carregar...</p>
      ) : (
        <>
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

          <div className={s.section}>
            <h2 className={s.sectionTitle}>Minhas Turmas</h2>
            {turmas.length === 0 ? (
              <p className={s.muted}>Nenhuma turma atribuída.</p>
            ) : (
              <div className={s.statsGrid}>
                {turmas.map((turma) => (
                  <div key={turma.id} className={s.statCard}>
                    <div
                      className={s.statIcon}
                      style={{ background: "#805AD520", color: "#805AD5" }}
                    >
                      <LayoutGrid size={24} />
                    </div>
                    <div>
                      <div className={s.statValue} style={{ fontSize: "1rem" }}>
                        {turma.nome}
                      </div>
                      <div className={s.statLabel}>
                        {turma.classe} &middot;{" "}
                        {turnoLabel[turma.turno] || turma.turno}
                        {turma.sala ? ` · Sala ${turma.sala}` : ""}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
