import { useEffect, useState } from "react";
import { Calendar } from "lucide-react";
import api from "@/shared/api/client";
import type {
  TurmaResponse,
  TurmaDetailResponse,
  HorarioAulaResponse,
  PaginatedResponse,
} from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

/* ── Constants ──────────────────────────────── */

const DIAS = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado"] as const;

const diaLabel: Record<string, string> = {
  segunda: "Segunda",
  terca: "Terça",
  quarta: "Quarta",
  quinta: "Quinta",
  sexta: "Sexta",
  sabado: "Sábado",
};

const TIME_SLOTS = [
  "07:00",
  "07:45",
  "08:30",
  "09:15",
  "10:00",
  "10:45",
  "11:30",
  "12:15",
  "13:00",
  "13:45",
  "14:30",
  "15:15",
  "16:00",
  "16:45",
  "17:30",
];

/* ── Types ──────────────────────────────────── */

interface ScheduleEntry extends HorarioAulaResponse {
  turma_nome: string;
}

/* ── Component ──────────────────────────────── */

export default function MeuHorario() {
  const { user } = useAuth();
  const [entries, setEntries] = useState<ScheduleEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.id) return;

    const load = async () => {
      try {
        const { data: turmasData } = await api.get<PaginatedResponse<TurmaResponse>>(
          "/turmas?limit=100",
        );

        const allEntries: ScheduleEntry[] = [];

        await Promise.all(
          turmasData.items.map(async (turma) => {
            try {
              const { data: detail } = await api.get<TurmaDetailResponse>(
                `/turmas/${turma.id}`,
              );
              for (const h of detail.horarios) {
                if (h.professor_id === user.id) {
                  allEntries.push({ ...h, turma_nome: turma.nome });
                }
              }
            } catch {
              // skip turma on error
            }
          }),
        );

        setEntries(allEntries);
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [user?.id]);

  /* Build lookup: dia -> time -> entries */
  const grid = new Map<string, ScheduleEntry[]>();
  for (const entry of entries) {
    const key = `${entry.dia_semana}_${entry.hora_inicio}`;
    if (!grid.has(key)) grid.set(key, []);
    grid.get(key)!.push(entry);
  }

  /* Determine which time slots actually have data */
  const activeSlots = TIME_SLOTS.filter((slot) =>
    DIAS.some((dia) => grid.has(`${dia}_${slot}`)),
  );
  const slotsToShow = activeSlots.length > 0 ? activeSlots : TIME_SLOTS.slice(0, 8);

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>Meu Horário</h1>
          <p className={s.subtitle}>Horário semanal de aulas</p>
        </div>
      </div>

      {loading ? (
        <p className={s.muted}>A carregar horários...</p>
      ) : entries.length === 0 ? (
        <div className={s.emptyState}>
          <div className={s.emptyIcon}>
            <Calendar size={48} />
          </div>
          <p>Nenhum horário atribuído.</p>
        </div>
      ) : (
        <div className={s.scheduleGrid}>
          {/* Header row */}
          <div className={s.scheduleHeader}>Hora</div>
          {DIAS.map((dia) => (
            <div key={dia} className={s.scheduleHeader}>
              {diaLabel[dia]}
            </div>
          ))}

          {/* Time rows */}
          {slotsToShow.map((slot) => (
            <>
              <div key={`time-${slot}`} className={s.scheduleTime}>
                {slot}
              </div>
              {DIAS.map((dia) => {
                const cellEntries = grid.get(`${dia}_${slot}`) || [];
                return (
                  <div key={`${dia}-${slot}`} className={s.scheduleCell}>
                    {cellEntries.map((entry) => (
                      <div key={entry.id} className={s.scheduleItem}>
                        <div className={s.scheduleItemName}>
                          {entry.turma_nome}
                        </div>
                        <div>
                          {entry.disciplina_id.length > 8
                            ? `${entry.disciplina_id.slice(0, 8)}...`
                            : entry.disciplina_id}
                        </div>
                        <div>
                          {entry.hora_inicio}–{entry.hora_fim}
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
