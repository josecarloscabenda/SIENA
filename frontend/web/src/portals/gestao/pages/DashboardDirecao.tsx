import { useEffect, useState } from "react";
import { Users, Users2, LayoutGrid, FileText } from "lucide-react";
import api from "@/shared/api/client";
import type { PaginatedResponse } from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

interface Stats {
  alunos: number;
  professores: number;
  turmas: number;
  matriculasPendentes: number;
}

export default function DashboardDirecao() {
  const { user } = useAuth();
  const [stats, setStats] = useState<Stats>({
    alunos: 0,
    professores: 0,
    turmas: 0,
    matriculasPendentes: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get<PaginatedResponse<unknown>>("/alunos?limit=1"),
      api.get<PaginatedResponse<unknown>>("/professores?limit=1"),
      api.get<PaginatedResponse<unknown>>("/turmas?limit=1"),
      api.get<PaginatedResponse<unknown>>("/matriculas?limit=1&estado=pendente"),
    ])
      .then(([alunos, professores, turmas, matriculas]) => {
        setStats({
          alunos: alunos.data.total,
          professores: professores.data.total,
          turmas: turmas.data.total,
          matriculasPendentes: matriculas.data.total,
        });
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const cards = [
    {
      label: "Total Alunos",
      value: stats.alunos,
      icon: Users,
      color: "#1A3F7A",
    },
    {
      label: "Total Professores",
      value: stats.professores,
      icon: Users2,
      color: "#00A878",
    },
    {
      label: "Total Turmas",
      value: stats.turmas,
      icon: LayoutGrid,
      color: "#805AD5",
    },
    {
      label: "Matrículas Pendentes",
      value: stats.matriculasPendentes,
      icon: FileText,
      color: "#DD6B20",
    },
  ];

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

      {loading ? (
        <p className={s.muted}>A carregar...</p>
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
