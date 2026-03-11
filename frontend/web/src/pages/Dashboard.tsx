import { useEffect, useState } from "react";
import { School, Users, BookOpen, Award } from "lucide-react";
import api from "@/shared/api/client";
import type { EscolaResponse, PaginatedResponse } from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import styles from "./Dashboard.module.css";

export default function Dashboard() {
  const { user } = useAuth();
  const [escolas, setEscolas] = useState<EscolaResponse[]>([]);
  const [totalEscolas, setTotalEscolas] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<PaginatedResponse<EscolaResponse>>("/escolas?limit=5")
      .then(({ data }) => {
        setEscolas(data.items);
        setTotalEscolas(data.total);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const stats = [
    { label: "Escolas", value: totalEscolas, icon: School, color: "#1A3F7A" },
    { label: "Alunos", value: 0, icon: Users, color: "#00A878" },
    { label: "Professores", value: 0, icon: BookOpen, color: "#DD6B20" },
    { label: "Turmas", value: 0, icon: Award, color: "#805AD5" },
  ];

  const tipoLabel: Record<string, string> = {
    publica: "Pública",
    privada: "Privada",
    comparticipada: "Comparticipada",
  };

  const nivelLabel: Record<string, string> = {
    primario: "Primário",
    secundario_1ciclo: "Secundário 1.º Ciclo",
    secundario_2ciclo: "Secundário 2.º Ciclo",
    tecnico: "Técnico",
  };

  return (
    <div>
      <div className={styles.pageHeader}>
        <h1 className={styles.pageTitle}>Dashboard</h1>
        <p className={styles.welcome}>
          Bem-vindo, <strong>{user?.nome_completo}</strong>
        </p>
      </div>

      {/* Stats cards */}
      <div className={styles.statsGrid}>
        {stats.map((stat) => (
          <div key={stat.label} className={styles.statCard}>
            <div
              className={styles.statIcon}
              style={{ backgroundColor: `${stat.color}15`, color: stat.color }}
            >
              <stat.icon size={24} />
            </div>
            <div>
              <div className={styles.statValue}>{stat.value}</div>
              <div className={styles.statLabel}>{stat.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Escolas list */}
      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>Escolas do Tenant</h2>
        {loading ? (
          <p className={styles.muted}>A carregar...</p>
        ) : escolas.length === 0 ? (
          <p className={styles.muted}>Nenhuma escola registada.</p>
        ) : (
          <div className={styles.escolasGrid}>
            {escolas.map((escola) => (
              <div key={escola.id} className={styles.escolaCard}>
                <div className={styles.escolaHeader}>
                  <School size={20} color="var(--primary)" />
                  <h3 className={styles.escolaNome}>{escola.nome}</h3>
                </div>
                <div className={styles.escolaDetails}>
                  <span>{tipoLabel[escola.tipo] || escola.tipo}</span>
                  <span className={styles.dot} />
                  <span>{nivelLabel[escola.nivel_ensino] || escola.nivel_ensino}</span>
                </div>
                <div className={styles.escolaLocation}>
                  {escola.municipio}, {escola.provincia}
                </div>
                {escola.codigo_sige && (
                  <div className={styles.escolaSige}>
                    SIGE: {escola.codigo_sige}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}