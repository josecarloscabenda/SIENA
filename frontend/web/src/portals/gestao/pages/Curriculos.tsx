import { useEffect, useState } from "react";
import { Plus, BookOpen, Code } from "lucide-react";
import api from "@/shared/api/client";
import type {
  CurriculoResponse,
  DisciplinaResponse,
  PaginatedResponse,
  AnoLetivoResponse,
  EscolaDetailResponse,
} from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

const nivelLabel: Record<string, string> = {
  primario: "Primário",
  secundario_1ciclo: "Sec. 1.º Ciclo",
  secundario_2ciclo: "Sec. 2.º Ciclo",
  tecnico: "Técnico",
};

export default function Curriculos() {
  useAuth();
  const [tab, setTab] = useState<"curriculos" | "disciplinas">("curriculos");

  /* Currículos */
  const [curriculos, setCurriculos] = useState<CurriculoResponse[]>([]);
  const [totalC, setTotalC] = useState(0);
  const [loadingC, setLoadingC] = useState(true);
  const [showFormC, setShowFormC] = useState(false);
  const [formC, setFormC] = useState({
    nivel: "primario",
    classe: "",
    ano_letivo_id: "",
    carga_horaria_total: 0,
  });

  /* Disciplinas */
  const [disciplinas, setDisciplinas] = useState<DisciplinaResponse[]>([]);
  const [totalD, setTotalD] = useState(0);
  const [loadingD, setLoadingD] = useState(true);
  const [showFormD, setShowFormD] = useState(false);
  const [formD, setFormD] = useState({
    nome: "",
    codigo: "",
    curriculo_id: "",
    carga_horaria_semanal: 0,
  });

  const [anosLetivos, setAnosLetivos] = useState<AnoLetivoResponse[]>([]);
  const [error, setError] = useState("");

  /* Map curriculo_id → display label */
  const curriculoMap = new Map(
    curriculos.map((c) => [c.id, `${nivelLabel[c.nivel] || c.nivel} - Classe ${c.classe}`])
  );

  const fetchCurriculos = () => {
    setLoadingC(true);
    api
      .get<PaginatedResponse<CurriculoResponse>>("/curriculos?offset=0&limit=50")
      .then(({ data }) => {
        setCurriculos(data.items);
        setTotalC(data.total);
      })
      .catch(() => {})
      .finally(() => setLoadingC(false));
  };

  const fetchDisciplinas = () => {
    setLoadingD(true);
    api
      .get<PaginatedResponse<DisciplinaResponse>>("/disciplinas?offset=0&limit=100")
      .then(({ data }) => {
        setDisciplinas(data.items);
        setTotalD(data.total);
      })
      .catch(() => {})
      .finally(() => setLoadingD(false));
  };

  useEffect(() => {
    fetchCurriculos();
    fetchDisciplinas();
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

  const handleCreateCurriculo = () => {
    setError("");
    api
      .post("/curriculos", {
        nivel: formC.nivel,
        classe: formC.classe,
        ano_letivo_id: formC.ano_letivo_id,
        carga_horaria_total: Number(formC.carga_horaria_total),
      })
      .then(() => {
        setShowFormC(false);
        setFormC({ nivel: "primario", classe: "", ano_letivo_id: "", carga_horaria_total: 0 });
        fetchCurriculos();
      })
      .catch((e) => setError(e.response?.data?.detail || "Erro ao criar currículo"));
  };

  const handleCreateDisciplina = () => {
    setError("");
    api
      .post("/disciplinas", {
        nome: formD.nome,
        codigo: formD.codigo,
        curriculo_id: formD.curriculo_id,
        carga_horaria_semanal: Number(formD.carga_horaria_semanal),
      })
      .then(() => {
        setShowFormD(false);
        setFormD({ nome: "", codigo: "", curriculo_id: "", carga_horaria_semanal: 0 });
        fetchDisciplinas();
      })
      .catch((e) => setError(e.response?.data?.detail || "Erro ao criar disciplina"));
  };

  /* Group disciplinas by curriculo */
  const discByCurriculo = new Map<string, DisciplinaResponse[]>();
  for (const d of disciplinas) {
    if (!discByCurriculo.has(d.curriculo_id)) discByCurriculo.set(d.curriculo_id, []);
    discByCurriculo.get(d.curriculo_id)!.push(d);
  }

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>Currículos &amp; Disciplinas</h1>
          <p className={s.subtitle}>
            {tab === "curriculos"
              ? `${totalC} currículo(s) registado(s)`
              : `${totalD} disciplina(s) registada(s)`}
          </p>
        </div>
        {tab === "curriculos" ? (
          <button className={s.addBtn} onClick={() => { setShowFormC(true); setError(""); }}>
            <Plus size={18} />
            Novo Currículo
          </button>
        ) : (
          <button className={s.addBtn} onClick={() => { setShowFormD(true); setError(""); }}>
            <Plus size={18} />
            Nova Disciplina
          </button>
        )}
      </div>

      <div className={s.tabs}>
        <button
          className={`${s.tab} ${tab === "curriculos" ? s.tabActive : ""}`}
          onClick={() => setTab("curriculos")}
        >
          <BookOpen size={14} style={{ marginRight: 6 }} />
          Currículos
        </button>
        <button
          className={`${s.tab} ${tab === "disciplinas" ? s.tabActive : ""}`}
          onClick={() => setTab("disciplinas")}
        >
          <Code size={14} style={{ marginRight: 6 }} />
          Disciplinas
        </button>
      </div>

      {error && <div className={s.error}>{error}</div>}

      {/* ── Currículos Tab ── */}
      {tab === "curriculos" && (
        <>
          {showFormC && (
            <div className={s.form} style={{ marginBottom: 20 }}>
              <h2 className={s.sectionTitle}>Novo Currículo</h2>
              <div className={s.formGrid}>
                <div className={s.field}>
                  <label className={s.label}>Nível</label>
                  <select
                    className={s.input}
                    value={formC.nivel}
                    onChange={(e) => setFormC({ ...formC, nivel: e.target.value })}
                  >
                    {Object.entries(nivelLabel).map(([k, v]) => (
                      <option key={k} value={k}>{v}</option>
                    ))}
                  </select>
                </div>
                <div className={s.field}>
                  <label className={s.label}>Classe</label>
                  <input
                    className={s.input}
                    value={formC.classe}
                    onChange={(e) => setFormC({ ...formC, classe: e.target.value })}
                    placeholder="Ex: 7"
                  />
                </div>
                <div className={s.field}>
                  <label className={s.label}>Ano Letivo</label>
                  <select
                    className={s.input}
                    value={formC.ano_letivo_id}
                    onChange={(e) => setFormC({ ...formC, ano_letivo_id: e.target.value })}
                  >
                    <option value="">Selecionar...</option>
                    {anosLetivos.map((al) => (
                      <option key={al.id} value={al.id}>{al.designacao} ({al.ano})</option>
                    ))}
                  </select>
                </div>
                <div className={s.field}>
                  <label className={s.label}>Carga Horária Total</label>
                  <input
                    type="number"
                    className={s.input}
                    value={formC.carga_horaria_total}
                    onChange={(e) => setFormC({ ...formC, carga_horaria_total: Number(e.target.value) })}
                  />
                </div>
              </div>
              <div className={s.formActions}>
                <button className={s.cancelBtn} onClick={() => setShowFormC(false)}>Cancelar</button>
                <button className={s.primaryBtn} onClick={handleCreateCurriculo}>Guardar</button>
              </div>
            </div>
          )}

          {loadingC ? (
            <p className={s.muted}>A carregar...</p>
          ) : curriculos.length === 0 ? (
            <p className={s.muted}>Nenhum currículo encontrado.</p>
          ) : (
            <div className={s.table}>
              <table>
                <thead>
                  <tr>
                    <th>Nível</th>
                    <th>Classe</th>
                    <th>Carga Horária</th>
                    <th>Disciplinas</th>
                  </tr>
                </thead>
                <tbody>
                  {curriculos.map((c) => {
                    const discs = discByCurriculo.get(c.id) || [];
                    return (
                      <tr key={c.id}>
                        <td>{nivelLabel[c.nivel] || c.nivel}</td>
                        <td style={{ fontWeight: 600 }}>Classe {c.classe}</td>
                        <td>{c.carga_horaria_total}h</td>
                        <td>
                          {discs.length === 0 ? (
                            <span className={s.muted}>Nenhuma</span>
                          ) : (
                            <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                              {discs.map((d) => (
                                <span key={d.id} className={`${s.badge} ${s.badgeBlue}`}>
                                  {d.codigo}
                                </span>
                              ))}
                            </div>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {/* ── Disciplinas Tab ── */}
      {tab === "disciplinas" && (
        <>
          {showFormD && (
            <div className={s.form} style={{ marginBottom: 20 }}>
              <h2 className={s.sectionTitle}>Nova Disciplina</h2>
              <div className={s.formGrid}>
                <div className={s.field}>
                  <label className={s.label}>Nome</label>
                  <input
                    className={s.input}
                    value={formD.nome}
                    onChange={(e) => setFormD({ ...formD, nome: e.target.value })}
                    placeholder="Ex: Matemática"
                  />
                </div>
                <div className={s.field}>
                  <label className={s.label}>Código</label>
                  <input
                    className={s.input}
                    value={formD.codigo}
                    onChange={(e) => setFormD({ ...formD, codigo: e.target.value })}
                    placeholder="Ex: MAT7"
                  />
                </div>
                <div className={s.field}>
                  <label className={s.label}>Currículo</label>
                  <select
                    className={s.input}
                    value={formD.curriculo_id}
                    onChange={(e) => setFormD({ ...formD, curriculo_id: e.target.value })}
                  >
                    <option value="">Selecionar...</option>
                    {curriculos.map((c) => (
                      <option key={c.id} value={c.id}>
                        {nivelLabel[c.nivel] || c.nivel} - Classe {c.classe}
                      </option>
                    ))}
                  </select>
                </div>
                <div className={s.field}>
                  <label className={s.label}>CH Semanal (horas)</label>
                  <input
                    type="number"
                    className={s.input}
                    value={formD.carga_horaria_semanal}
                    onChange={(e) => setFormD({ ...formD, carga_horaria_semanal: Number(e.target.value) })}
                  />
                </div>
              </div>
              <div className={s.formActions}>
                <button className={s.cancelBtn} onClick={() => setShowFormD(false)}>Cancelar</button>
                <button className={s.primaryBtn} onClick={handleCreateDisciplina}>Guardar</button>
              </div>
            </div>
          )}

          {loadingD ? (
            <p className={s.muted}>A carregar...</p>
          ) : disciplinas.length === 0 ? (
            <p className={s.muted}>Nenhuma disciplina encontrada.</p>
          ) : (
            <div className={s.table}>
              <table>
                <thead>
                  <tr>
                    <th>Nome</th>
                    <th>Código</th>
                    <th>Currículo</th>
                    <th>CH Semanal</th>
                  </tr>
                </thead>
                <tbody>
                  {disciplinas.map((d) => (
                    <tr key={d.id}>
                      <td style={{ fontWeight: 600 }}>{d.nome}</td>
                      <td><span className={`${s.badge} ${s.badgeBlue}`}>{d.codigo}</span></td>
                      <td>{curriculoMap.get(d.curriculo_id) || "—"}</td>
                      <td>{d.carga_horaria_semanal}h</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}
