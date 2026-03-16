import { useEffect, useState } from "react";
import { Calendar } from "lucide-react";
import api from "@/shared/api/client";
import type {
  TurmaResponse,
  HorarioAulaResponse,
  PaginatedResponse,
} from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

const DIAS_SEMANA = ["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado"];

const TIME_SLOTS = [
  "07:00",
  "08:00",
  "09:00",
  "10:00",
  "11:00",
  "12:00",
  "13:00",
  "14:00",
  "15:00",
  "16:00",
];

export default function HorarioAluno() {
  useAuth();
  const [horarios, setHorarios] = useState<HorarioAulaResponse[]>([]);
  const [turma, setTurma] = useState<TurmaResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [noData, setNoData] = useState(false);

  useEffect(() => {
    api
      .get<PaginatedResponse<TurmaResponse>>("/turmas?limit=10")
      .then((res) => {
        const turmas = res.data.items;
        if (turmas.length === 0) {
          setNoData(true);
          return;
        }
        const firstTurma = turmas[0];
        setTurma(firstTurma);
        return api.get<HorarioAulaResponse[]>(
          `/turmas/${firstTurma.id}/horarios`
        );
      })
      .then((res) => {
        if (res) setHorarios(res.data);
      })
      .catch(() => {
        setNoData(true);
      })
      .finally(() => setLoading(false));
  }, []);

  const getHorarioForSlot = (dia: string, time: string) => {
    return horarios.filter((h) => {
      const diaMatch =
        h.dia_semana.toLowerCase() === dia.toLowerCase();
      const hourStart = h.hora_inicio.slice(0, 5);
      return diaMatch && hourStart === time;
    });
  };

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>Horario</h1>
          <p className={s.subtitle}>
            {turma
              ? `Turma: ${turma.nome} - ${turma.classe} (${turma.turno})`
              : "O seu horario semanal"}
          </p>
        </div>
      </div>

      {loading ? (
        <p className={s.muted}>A carregar...</p>
      ) : noData ? (
        <div className={s.emptyState}>
          <div className={s.emptyIcon}>
            <Calendar size={48} />
          </div>
          <p>
            O seu horario sera disponibilizado apos alocacao na turma.
          </p>
        </div>
      ) : (
        <div className={s.scheduleGrid}>
          {/* Header row */}
          <div className={s.scheduleHeader}>Hora</div>
          {DIAS_SEMANA.map((dia) => (
            <div key={dia} className={s.scheduleHeader}>
              {dia}
            </div>
          ))}

          {/* Time slot rows */}
          {TIME_SLOTS.map((time) => (
            <>
              <div key={`time-${time}`} className={s.scheduleTime}>
                {time}
              </div>
              {DIAS_SEMANA.map((dia) => {
                const items = getHorarioForSlot(dia, time);
                return (
                  <div
                    key={`${dia}-${time}`}
                    className={s.scheduleCell}
                  >
                    {items.map((item) => (
                      <div key={item.id} className={s.scheduleItem}>
                        <div className={s.scheduleItemName}>
                          {item.disciplina_id.slice(0, 8)}...
                        </div>
                        <div>
                          {item.hora_inicio.slice(0, 5)} -{" "}
                          {item.hora_fim.slice(0, 5)}
                        </div>
                      </div>
                    ))}
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
