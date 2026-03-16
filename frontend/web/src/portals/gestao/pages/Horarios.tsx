import { useEffect, useState } from "react";
import { Plus, Clock } from "lucide-react";
import api from "@/shared/api/client";
import type {
  TurmaResponse,
  HorarioAulaResponse,
  DisciplinaResponse,
  ProfessorResponse,
  PaginatedResponse,
} from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

const DIAS = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado"] as const;
const DIA_LABELS: Record<string, string> = {
  segunda: "Segunda",
  terca: "Terça",
  quarta: "Quarta",
  quinta: "Quinta",
  sexta: "Sexta",
  sabado: "Sábado",
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

export default function Horarios() {
  useAuth(); // ensure authenticated
  const [turmas, setTurmas] = useState<TurmaResponse[]>([]);
  const [selectedTurma, setSelectedTurma] = useState("");
  const [horarios, setHorarios] = useState<HorarioAulaResponse[]>([]);
  const [disciplinas, setDisciplinas] = useState<DisciplinaResponse[]>([]);
  const [professores, setProfessores] = useState<ProfessorResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    disciplina_id: "",
    professor_id: "",
    dia_semana: "segunda",
    hora_inicio: "07:30",
    hora_fim: "08:15",
  });

  /* Discipline map for display */
  const discMap = new Map(disciplinas.map((d) => [d.id, d.nome]));

  useEffect(() => {
    api
      .get<PaginatedResponse<TurmaResponse>>("/turmas?limit=100")
      .then(({ data }) => setTurmas(data.items))
      .catch(() => {});
    api
      .get<PaginatedResponse<DisciplinaResponse>>("/disciplinas?offset=0&limit=100")
      .then(({ data }) => setDisciplinas(data.items))
      .catch(() => {});
    api
      .get<PaginatedResponse<ProfessorResponse>>("/professores?offset=0&limit=100")
      .then(({ data }) => setProfessores(data.items))
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!selectedTurma) {
      setHorarios([]);
      return;
    }
    setLoading(true);
    api
      .get<HorarioAulaResponse[]>(`/turmas/${selectedTurma}/horarios`)
      .then(({ data }) => setHorarios(data))
      .catch(() => setHorarios([]))
      .finally(() => setLoading(false));
  }, [selectedTurma]);

  /* Backend returns time as "HH:MM:SS", TIME_SLOTS use "HH:MM" */
  const trimTime = (t: string) => t.slice(0, 5);

  const findLesson = (dia: string, inicio: string, fim: string) =>
    horarios.find(
      (h) => h.dia_semana === dia && trimTime(h.hora_inicio) === inicio && trimTime(h.hora_fim) === fim,
    );

  const handleAdd = () => {
    setError("");
    api
      .post(`/turmas/${selectedTurma}/horarios`, {
        disciplina_id: form.disciplina_id,
        professor_id: form.professor_id,
        dia_semana: form.dia_semana,
        hora_inicio: form.hora_inicio,
        hora_fim: form.hora_fim,
      })
      .then(() => {
        setShowForm(false);
        setForm({ disciplina_id: "", professor_id: "", dia_semana: "segunda", hora_inicio: "07:30", hora_fim: "08:15" });
        /* Refresh */
        api
          .get<HorarioAulaResponse[]>(`/turmas/${selectedTurma}/horarios`)
          .then(({ data }) => setHorarios(data))
          .catch(() => {});
      })
      .catch((e) => setError(e.response?.data?.detail || "Erro ao adicionar aula"));
  };

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>Horários</h1>
          <p className={s.subtitle}>Gestão de horários por turma</p>
        </div>
        {selectedTurma && (
          <button className={s.addBtn} onClick={() => { setShowForm(true); setError(""); }}>
            <Plus size={18} />
            Adicionar Aula
          </button>
        )}
      </div>

      {/* Turma selector */}
      <div style={{ marginBottom: 20 }}>
        <label className={s.label} style={{ marginRight: 8 }}>Turma</label>
        <select
          className={s.input}
          style={{ minWidth: 260 }}
          value={selectedTurma}
          onChange={(e) => setSelectedTurma(e.target.value)}
        >
          <option value="">Selecionar turma...</option>
          {turmas.map((t) => (
            <option key={t.id} value={t.id}>
              {t.nome} - Classe {t.classe} ({t.turno})
            </option>
          ))}
        </select>
      </div>

      {error && <div className={s.error}>{error}</div>}

      {/* Add form */}
      {showForm && selectedTurma && (
        <div className={s.form} style={{ marginBottom: 20 }}>
          <h2 className={s.sectionTitle}>Adicionar Aula</h2>
          <div className={s.formGrid}>
            <div className={s.field}>
              <label className={s.label}>Disciplina</label>
              <select
                className={s.input}
                value={form.disciplina_id}
                onChange={(e) => setForm({ ...form, disciplina_id: e.target.value })}
              >
                <option value="">Selecionar...</option>
                {disciplinas.map((d) => (
                  <option key={d.id} value={d.id}>{d.nome} ({d.codigo})</option>
                ))}
              </select>
            </div>
            <div className={s.field}>
              <label className={s.label}>Professor</label>
              <select
                className={s.input}
                value={form.professor_id}
                onChange={(e) => setForm({ ...form, professor_id: e.target.value })}
              >
                <option value="">Selecionar...</option>
                {professores.map((p) => (
                  <option key={p.id} value={p.id}>{p.pessoa.nome_completo}</option>
                ))}
              </select>
            </div>
            <div className={s.field}>
              <label className={s.label}>Dia da Semana</label>
              <select
                className={s.input}
                value={form.dia_semana}
                onChange={(e) => setForm({ ...form, dia_semana: e.target.value })}
              >
                {DIAS.map((d) => (
                  <option key={d} value={d}>{DIA_LABELS[d]}</option>
                ))}
              </select>
            </div>
            <div className={s.field}>
              <label className={s.label}>Hora Início</label>
              <input
                type="time"
                className={s.input}
                value={form.hora_inicio}
                onChange={(e) => setForm({ ...form, hora_inicio: e.target.value })}
              />
            </div>
            <div className={s.field}>
              <label className={s.label}>Hora Fim</label>
              <input
                type="time"
                className={s.input}
                value={form.hora_fim}
                onChange={(e) => setForm({ ...form, hora_fim: e.target.value })}
              />
            </div>
          </div>
          <div className={s.formActions}>
            <button className={s.cancelBtn} onClick={() => setShowForm(false)}>Cancelar</button>
            <button className={s.primaryBtn} onClick={handleAdd}>Guardar</button>
          </div>
        </div>
      )}

      {/* Schedule grid */}
      {!selectedTurma ? (
        <div className={s.emptyState}>
          <div className={s.emptyIcon}><Clock size={48} /></div>
          <p>Selecione uma turma para visualizar o horário.</p>
        </div>
      ) : loading ? (
        <p className={s.muted}>A carregar...</p>
      ) : (
        <div className={s.scheduleGrid}>
          {/* Header row */}
          <div className={s.scheduleHeader}>Hora</div>
          {DIAS.map((d) => (
            <div key={d} className={s.scheduleHeader}>{DIA_LABELS[d]}</div>
          ))}

          {/* Time slot rows */}
          {TIME_SLOTS.map((slot) => (
            <>
              <div key={`t-${slot.inicio}`} className={s.scheduleTime}>
                {slot.inicio}
                <br />
                {slot.fim}
              </div>
              {DIAS.map((dia) => {
                const lesson = findLesson(dia, slot.inicio, slot.fim);
                return (
                  <div key={`${dia}-${slot.inicio}`} className={s.scheduleCell}>
                    {lesson && (
                      <div className={s.scheduleItem}>
                        <div className={s.scheduleItemName}>
                          {discMap.get(lesson.disciplina_id) || "—"}
                        </div>
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
