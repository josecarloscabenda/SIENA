import { useEffect, useState } from "react";
import { Plus, Search, LayoutGrid, Eye } from "lucide-react";
import api from "@/shared/api/client";
import type {
  TurmaResponse,
  TurmaDetailResponse,
  ProfessorResponse,
  AnoLetivoResponse,
  EscolaDetailResponse,
  DisciplinaResponse,
  PaginatedResponse,
} from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

interface TurmaForm {
  nome: string;
  classe: string;
  turno: string;
  ano_letivo_id: string;
  capacidade_max: number;
  professor_regente_id: string;
  sala: string;
}

const emptyForm: TurmaForm = {
  nome: "",
  classe: "",
  turno: "matutino",
  ano_letivo_id: "",
  capacidade_max: 40,
  professor_regente_id: "",
  sala: "",
};

const turnoLabel: Record<string, string> = {
  matutino: "Matutino",
  vespertino: "Vespertino",
  nocturno: "Nocturno",
};

const DIA_LABELS: Record<string, string> = {
  segunda: "Seg",
  terca: "Ter",
  quarta: "Qua",
  quinta: "Qui",
  sexta: "Sex",
  sabado: "Sáb",
};

export default function Turmas() {
  const { hasRole } = useAuth();
  const [turmas, setTurmas] = useState<TurmaResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<TurmaForm>(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  /* Lookups */
  const [professores, setProfessores] = useState<ProfessorResponse[]>([]);
  const [anosLetivos, setAnosLetivos] = useState<AnoLetivoResponse[]>([]);
  const profMap = new Map(professores.map((p) => [p.id, p.pessoa.nome_completo]));

  /* Detail view */
  const [detailTurma, setDetailTurma] = useState<TurmaDetailResponse | null>(null);
  const [detailDisciplinas, setDetailDisciplinas] = useState<DisciplinaResponse[]>([]);
  const [, setLoadingDetail] = useState(false);

  const canManage = hasRole("super_admin", "diretor", "secretaria");

  const fetchTurmas = () => {
    setLoading(true);
    api
      .get<PaginatedResponse<TurmaResponse>>("/turmas?offset=0&limit=50")
      .then(({ data }) => {
        setTurmas(data.items);
        setTotal(data.total);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchTurmas();
    api
      .get<PaginatedResponse<ProfessorResponse>>("/professores?offset=0&limit=100")
      .then(({ data }) => setProfessores(data.items))
      .catch(() => {});
    /* Get anos letivos from escola detail */
    api
      .get<{ items: EscolaDetailResponse[] }>("/escolas?limit=1")
      .then(({ data }) => {
        if (data.items.length > 0) {
          return api.get<EscolaDetailResponse>(`/escolas/${data.items[0].id}`);
        }
        return null;
      })
      .then((res) => {
        if (res) setAnosLetivos(res.data.anos_letivos || []);
      })
      .catch(() => {});
  }, []);

  const openCreate = () => {
    setForm(emptyForm);
    setShowForm(true);
    setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      await api.post("/turmas", {
        ...form,
        capacidade_max: Number(form.capacidade_max),
      });
      setShowForm(false);
      fetchTurmas();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao criar turma.");
    } finally {
      setSaving(false);
    }
  };

  const openDetail = async (turmaId: string) => {
    setLoadingDetail(true);
    setDetailTurma(null);
    try {
      const { data } = await api.get<TurmaDetailResponse>(`/turmas/${turmaId}`);
      setDetailTurma(data);
      /* Also load disciplinas for reference */
      const { data: discData } = await api.get<PaginatedResponse<DisciplinaResponse>>("/disciplinas?offset=0&limit=100");
      setDetailDisciplinas(discData.items);
    } catch {
      setError("Erro ao carregar detalhes da turma");
    } finally {
      setLoadingDetail(false);
    }
  };

  const filtered = turmas.filter((t) => {
    const q = search.toLowerCase();
    return (
      t.nome.toLowerCase().includes(q) ||
      t.classe.toLowerCase().includes(q) ||
      (t.sala?.toLowerCase().includes(q) ?? false)
    );
  });

  const trimTime = (t: string) => t.slice(0, 5);

  /* Detail view */
  if (detailTurma) {
    const discMap = new Map(detailDisciplinas.map((d) => [d.id, d]));
    return (
      <div>
        <button className={s.backBtn} onClick={() => setDetailTurma(null)}>
          &larr; Voltar
        </button>
        <div className={s.pageHeader}>
          <div>
            <h1 className={s.pageTitle}>{detailTurma.nome}</h1>
            <p className={s.subtitle}>
              Classe {detailTurma.classe} — {turnoLabel[detailTurma.turno] || detailTurma.turno} — Cap. {detailTurma.capacidade_max} alunos
            </p>
          </div>
        </div>

        <div className={s.form} style={{ marginBottom: 20 }}>
          <h2 className={s.sectionTitle}>Informações</h2>
          <div className={s.formGrid}>
            <div className={s.field}>
              <label className={s.label}>Professor Regente</label>
              <div style={{ padding: "10px 0", fontWeight: 500 }}>
                {detailTurma.professor_regente_nome ||
                  profMap.get(detailTurma.professor_regente_id) ||
                  "—"}
              </div>
            </div>
            <div className={s.field}>
              <label className={s.label}>Ano Lectivo</label>
              <div style={{ padding: "10px 0", fontWeight: 500 }}>
                {detailTurma.ano_letivo_designacao || "—"}
              </div>
            </div>
            <div className={s.field}>
              <label className={s.label}>Sala</label>
              <div style={{ padding: "10px 0", fontWeight: 500 }}>{detailTurma.sala || "—"}</div>
            </div>
          </div>
        </div>

        <h2 className={s.sectionTitle}>Horários ({detailTurma.horarios?.length || 0})</h2>
        {(!detailTurma.horarios || detailTurma.horarios.length === 0) ? (
          <p className={s.muted}>Nenhum horário definido para esta turma.</p>
        ) : (
          <div className={s.table}>
            <table>
              <thead>
                <tr>
                  <th>Dia</th>
                  <th>Hora</th>
                  <th>Disciplina</th>
                  <th>Professor</th>
                </tr>
              </thead>
              <tbody>
                {detailTurma.horarios
                  .sort((a, b) => {
                    const dias = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado"];
                    return dias.indexOf(a.dia_semana) - dias.indexOf(b.dia_semana) || a.hora_inicio.localeCompare(b.hora_inicio);
                  })
                  .map((h) => (
                    <tr key={h.id}>
                      <td style={{ fontWeight: 600 }}>{DIA_LABELS[h.dia_semana] || h.dia_semana}</td>
                      <td>{trimTime(h.hora_inicio)} - {trimTime(h.hora_fim)}</td>
                      <td>{h.disciplina_nome || discMap.get(h.disciplina_id)?.nome || "—"}</td>
                      <td>{h.professor_nome || profMap.get(h.professor_id) || "—"}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    );
  }

  /* Create form */
  if (showForm) {
    return (
      <div>
        <button className={s.backBtn} onClick={() => setShowForm(false)}>
          &larr; Voltar
        </button>
        <h1 className={s.pageTitle}>Nova Turma</h1>

        {error && <div className={s.error}>{error}</div>}

        <form className={s.form} onSubmit={handleSubmit}>
          <div className={s.formGrid}>
            <div className={s.field}>
              <label className={s.label}>Nome</label>
              <input className={s.input} required value={form.nome} onChange={(e) => setForm({ ...form, nome: e.target.value })} placeholder="Ex: 7.ª A" />
            </div>
            <div className={s.field}>
              <label className={s.label}>Classe</label>
              <input className={s.input} required value={form.classe} onChange={(e) => setForm({ ...form, classe: e.target.value })} placeholder="Ex: 7" />
            </div>
            <div className={s.field}>
              <label className={s.label}>Turno</label>
              <select className={s.input} value={form.turno} onChange={(e) => setForm({ ...form, turno: e.target.value })}>
                <option value="matutino">Matutino</option>
                <option value="vespertino">Vespertino</option>
                <option value="nocturno">Nocturno</option>
              </select>
            </div>
            <div className={s.field}>
              <label className={s.label}>Ano Letivo</label>
              <select className={s.input} required value={form.ano_letivo_id} onChange={(e) => setForm({ ...form, ano_letivo_id: e.target.value })}>
                <option value="">Selecionar...</option>
                {anosLetivos.map((al) => (
                  <option key={al.id} value={al.id}>{al.designacao} ({al.ano})</option>
                ))}
              </select>
            </div>
            <div className={s.field}>
              <label className={s.label}>Capacidade Máxima</label>
              <input className={s.input} type="number" required value={form.capacidade_max} onChange={(e) => setForm({ ...form, capacidade_max: Number(e.target.value) })} />
            </div>
            <div className={s.field}>
              <label className={s.label}>Professor Regente</label>
              <select className={s.input} required value={form.professor_regente_id} onChange={(e) => setForm({ ...form, professor_regente_id: e.target.value })}>
                <option value="">Selecionar...</option>
                {professores.map((p) => (
                  <option key={p.id} value={p.id}>{p.pessoa.nome_completo} ({p.especialidade})</option>
                ))}
              </select>
            </div>
            <div className={s.field}>
              <label className={s.label}>Sala</label>
              <input className={s.input} value={form.sala} onChange={(e) => setForm({ ...form, sala: e.target.value })} placeholder="Ex: Sala 1A" />
            </div>
          </div>
          <div className={s.formActions}>
            <button type="button" className={s.cancelBtn} onClick={() => setShowForm(false)}>Cancelar</button>
            <button type="submit" className={s.primaryBtn} disabled={saving}>{saving ? "A guardar..." : "Guardar"}</button>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>Turmas</h1>
          <p className={s.subtitle}>{total} turma(s) registada(s)</p>
        </div>
        {canManage && (
          <button className={s.addBtn} onClick={openCreate}>
            <Plus size={18} />
            Nova Turma
          </button>
        )}
      </div>

      <div className={s.searchBar}>
        <Search size={18} color="var(--text-muted)" />
        <input
          type="text"
          placeholder="Pesquisar por nome, classe ou sala..."
          className={s.searchInput}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {error && <div className={s.error}>{error}</div>}

      {loading ? (
        <p className={s.muted}>A carregar...</p>
      ) : filtered.length === 0 ? (
        <p className={s.muted}>Nenhuma turma encontrada.</p>
      ) : (
        <div className={s.table}>
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>Classe</th>
                <th>Turno</th>
                <th>Professor Regente</th>
                <th>Capacidade</th>
                <th>Sala</th>
                <th>Acções</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((turma) => (
                <tr key={turma.id}>
                  <td>
                    <div className={s.nameCell}>
                      <LayoutGrid size={16} />
                      {turma.nome}
                    </div>
                  </td>
                  <td>{turma.classe}</td>
                  <td>{turnoLabel[turma.turno] || turma.turno}</td>
                  <td>
                    {turma.professor_regente_nome ||
                      profMap.get(turma.professor_regente_id) ||
                      "—"}
                  </td>
                  <td>{turma.capacidade_max}</td>
                  <td>{turma.sala || "—"}</td>
                  <td>
                    <button className={s.editBtn} onClick={() => openDetail(turma.id)}>
                      <Eye size={14} style={{ marginRight: 4 }} />
                      Ver
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
