import { useEffect, useState } from "react";
import { School, Globe } from "lucide-react";
import api from "@/shared/api/client";
import type { PaginatedResponse, EscolaResponse } from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

export default function DashboardAdmin() {
  const { user } = useAuth();
  const [totalEscolas, setTotalEscolas] = useState(0);

  useEffect(() => {
    api.get<PaginatedResponse<EscolaResponse>>("/escolas/all?limit=1")
      .then(({ data }) => setTotalEscolas(data.total))
      .catch(() => {});
  }, []);

  const stats = [
    { label: "Escolas", value: totalEscolas, icon: School, color: "#1a1a2e" },
    { label: "Plataforma", value: "SIENA", icon: Globe, color: "#e94560" },
  ];

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>Administracao da Plataforma</h1>
          <p className={s.subtitle}>Bem-vindo, {user?.nome_completo}</p>
        </div>
      </div>

      <div className={s.statsGrid}>
        {stats.map((stat) => (
          <div key={stat.label} className={s.statCard}>
            <div className={s.statIcon} style={{ backgroundColor: `${stat.color}15`, color: stat.color }}>
              <stat.icon size={24} />
            </div>
            <div>
              <div className={s.statValue}>{stat.value}</div>
              <div className={s.statLabel}>{stat.label}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
