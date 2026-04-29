import { useEffect, useState } from "react";
import {
  LayoutGrid,
  CalendarDays,
  BookOpen,
  Users,
  ClipboardList,
  Star,
  Clock,
} from "lucide-react";
import api from "@/shared/api/client";
import type { ProfessorStats } from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

const turnoLabel: Record<string, string> = {
  matutino: "Matutino",
  vespertino: "Vespertino",
  nocturno: "Nocturno",
};

const diaLabel: Record<string, string> = {
  segunda: "Seg",
  terca: "Ter",
  quarta: "Qua",
  quinta: "Qui",
  sexta: "Sex",
  sabado: "Sáb",
};

export default function DashboardProfessor() {
  const { user } = useAuth();
  const [stats, setStats] = useState<ProfessorStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user?.professor_id) {
      setLoading(false);
      setError("Utilizador sem perfil de professor.");
      return;
    }
    api
      .get<ProfessorStats>("/dashboard/professor")
      .then(({ data }) => setStats(data))
      .catch(() => setError("Não foi possível carregar o painel."))
      .finally(() => setLoading(false));
  }, [user?.professor_id]);

  if (loading) {
    return <p className={s.muted}>A carregar...</p>;
  }

  if (error || !stats) {
    return (
      <div>
        <h1 className={s.pageTitle}>Painel do Professor</h1>
        <p className={s.muted}>{error ?? "Sem dados."}</p>
      </div>
    );
  }

  const cards = [
    { label: "Turmas Atribuídas", value: stats.turmas_atribuidas, icon: LayoutGrid, color: "#1A3F7A" },
    { label: "Disciplinas que Lecciona", value: stats.disciplinas_lecciona, icon: BookOpen, color: "#805AD5" },
    { label: "Total de Alunos", value: stats.total_alunos, icon: Users, color: "#00A878" },
    { label: "Notas por Lançar", value: stats.notas_por_lancar, icon: ClipboardList, color: "#DD6B20" },
  ];

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>
            Bem-vindo{stats.nome ? `, Prof. ${stats.nome}` : ""}
          </h1>
          <p className={s.subtitle}>Painel do Professor</p>
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

      <div className={s.section} style={{ marginTop: 24 }}>
        <h2 className={s.sectionTitle}>
          <LayoutGrid size={18} style={{ marginRight: 8, verticalAlign: "middle" }} />
          Minhas Turmas
        </h2>
        {stats.turmas.length === 0 ? (
          <p className={s.muted}>Nenhuma turma atribuída.</p>
        ) : (
          <div className={s.table}>
            <table>
              <thead>
                <tr>
                  <th>Turma</th>
                  <th>Classe</th>
                  <th>Turno</th>
                  <th>Disciplinas</th>
                  <th>Alunos</th>
                  <th>Regência</th>
                </tr>
              </thead>
              <tbody>
                {stats.turmas.map((t) => (
                  <tr key={t.turma_id}>
                    <td><strong>{t.nome}</strong></td>
                    <td>{t.classe}</td>
                    <td>{turnoLabel[t.turno] || t.turno}</td>
                    <td>{t.leciona_disciplinas}</td>
                    <td>{t.total_alunos}</td>
                    <td>
                      {t.is_regente ? (
                        <span className={`${s.badge} ${s.badgeYellow}`}>
                          <Star size={12} style={{ marginRight: 4, verticalAlign: "middle" }} />
                          Regente
                        </span>
                      ) : (
                        <span className={s.muted}>—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className={s.section} style={{ marginTop: 24 }}>
        <h2 className={s.sectionTitle}>
          <CalendarDays size={18} style={{ marginRight: 8, verticalAlign: "middle" }} />
          Próximas Aulas
        </h2>
        {stats.proximas_aulas.length === 0 ? (
          <p className={s.muted}>Sem aulas agendadas.</p>
        ) : (
          <div className={s.table}>
            <table>
              <thead>
                <tr>
                  <th>Dia</th>
                  <th>Hora</th>
                  <th>Turma</th>
                  <th>Disciplina</th>
                </tr>
              </thead>
              <tbody>
                {stats.proximas_aulas.map((aula) => (
                  <tr key={aula.horario_id}>
                    <td>{diaLabel[aula.dia_semana] || aula.dia_semana}</td>
                    <td>
                      <Clock size={12} style={{ marginRight: 4, verticalAlign: "middle" }} />
                      {aula.hora_inicio} – {aula.hora_fim}
                    </td>
                    <td><strong>{aula.turma_nome}</strong></td>
                    <td>{aula.disciplina_nome}</td>
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
