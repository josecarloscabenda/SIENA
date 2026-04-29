import { useEffect, useState } from "react";
import { Calendar, AlertTriangle } from "lucide-react";
import api from "@/shared/api/client";
import type { AlunoStats, HorarioAulaResponse } from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

const DIAS = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado"] as const;
const DIA_LABELS: Record<string, string> = {
  segunda: "Seg",
  terca: "Ter",
  quarta: "Qua",
  quinta: "Qui",
  sexta: "Sex",
  sabado: "Sáb",
};

const TIME_SLOTS = [
  { inicio: "07:30", fim: "08:15" },
  { inicio: "08:15", fim: "09:00" },
  { inicio: "09:00", fim: "09:45" },
  { inicio: "09:45", fim: "10:30" },
  { inicio: "10:45", fim: "11:30" },
  { inicio: "11:30", fim: "12:15" },
  { inicio: "12:15", fim: "13:00" },
  { inicio: "13:00", fim: "13:45" },
  { inicio: "14:00", fim: "14:45" },
  { inicio: "14:45", fim: "15:30" },
  { inicio: "15:30", fim: "16:15" },
  { inicio: "16:15", fim: "17:00" },
];

export default function HorarioAluno() {
  const { user } = useAuth();
  const [horarios, setHorarios] = useState<HorarioAulaResponse[]>([]);
  const [aluno, setAluno] = useState<AlunoStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user?.aluno_id) {
      setLoading(false);
      setError("O seu perfil de aluno ainda não está associado.");
      return;
    }
    setLoading(true);
    api
      .get<AlunoStats>("/dashboard/aluno")
      .then(({ data }) => {
        setAluno(data);
        if (!data.turma_id) {
          setError("Ainda não está alocado a uma turma.");
          setLoading(false);
          return;
        }
        return api.get<HorarioAulaResponse[]>(`/turmas/${data.turma_id}/horarios`);
      })
      .then((res) => {
        if (res) setHorarios(res.data);
      })
      .catch(() => setError("Não foi possível carregar o horário."))
      .finally(() => setLoading(false));
  }, [user?.aluno_id]);

  const trim = (t: string) => t.slice(0, 5);

  const findLesson = (dia: string, inicio: string, fim: string) =>
    horarios.find(
      (h) =>
        h.dia_semana === dia &&
        trim(h.hora_inicio) === inicio &&
        trim(h.hora_fim) === fim,
    );

  if (loading) return <p className={s.muted}>A carregar...</p>;

  if (error) {
    return (
      <div>
        <h1 className={s.pageTitle}>Horário</h1>
        <div className={s.emptyState}>
          <div className={s.emptyIcon}>
            <AlertTriangle size={48} />
          </div>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>Horário</h1>
          <p className={s.subtitle}>
            <Calendar size={14} style={{ verticalAlign: "middle", marginRight: 4 }} />
            {aluno?.classe ? `${aluno.classe} ` : ""}
            {aluno?.turma_nome ? `(${aluno.turma_nome})` : ""}
          </p>
        </div>
      </div>

      {horarios.length === 0 ? (
        <div className={s.emptyState}>
          <div className={s.emptyIcon}>
            <Calendar size={48} />
          </div>
          <p>Sem aulas registadas no horário desta turma.</p>
        </div>
      ) : (
        <div className={s.scheduleGrid}>
          <div className={s.scheduleHeader}>Hora</div>
          {DIAS.map((d) => (
            <div key={d} className={s.scheduleHeader}>
              {DIA_LABELS[d]}
            </div>
          ))}

          {TIME_SLOTS.map((slot) => (
            <>
              <div key={`t-${slot.inicio}`} className={s.scheduleTime}>
                {slot.inicio}
                <br />
                {slot.fim}
              </div>
              {DIAS.map((d) => {
                const lesson = findLesson(d, slot.inicio, slot.fim);
                return (
                  <div
                    key={`${d}-${slot.inicio}`}
                    className={s.scheduleCell}
                  >
                    {lesson && (
                      <div className={s.scheduleItem}>
                        <div className={s.scheduleItemName}>
                          {lesson.disciplina_nome || "—"}
                        </div>
                        {lesson.professor_nome && (
                          <div className={s.scheduleItemSub}>
                            {lesson.professor_nome}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </>
          ))}
        </div>
      )}
    </div>
  );
}
