import { useState } from "react";
import { Search, FileText, AlertTriangle } from "lucide-react";
import api from "@/shared/api/client";
import type { BoletimResponse, FaltaResumoResponse } from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

export default function EncarregadoView() {
  useAuth();
  const [alunoId, setAlunoId] = useState("");
  const [periodo, setPeriodo] = useState(1);
  const [boletim, setBoletim] = useState<BoletimResponse | null>(null);
  const [resumo, setResumo] = useState<FaltaResumoResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [consulted, setConsulted] = useState(false);

  const handleConsultar = () => {
    if (!alunoId.trim()) return;

    setLoading(true);
    setError("");
    setBoletim(null);
    setResumo(null);
    setConsulted(true);

    Promise.all([
      api
        .get<BoletimResponse>(
          `/alunos/${alunoId.trim()}/boletim?periodo=${periodo}`
        )
        .catch(() => null),
      api
        .get<FaltaResumoResponse>(`/alunos/${alunoId.trim()}/faltas/resumo`)
        .catch(() => null),
    ])
      .then(([boletimRes, resumoRes]) => {
        if (!boletimRes && !resumoRes) {
          setError(
            "Nao foi possivel encontrar dados para este aluno. Verifique o ID e tente novamente."
          );
          return;
        }
        if (boletimRes) setBoletim(boletimRes.data);
        if (resumoRes) setResumo(resumoRes.data);
      })
      .finally(() => setLoading(false));
  };

  const handlePeriodoChange = (p: number) => {
    setPeriodo(p);
    if (consulted && alunoId.trim()) {
      setLoading(true);
      setError("");

      api
        .get<BoletimResponse>(
          `/alunos/${alunoId.trim()}/boletim?periodo=${p}`
        )
        .then((res) => setBoletim(res.data))
        .catch(() => setBoletim(null))
        .finally(() => setLoading(false));
    }
  };

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>Portal do Encarregado</h1>
          <p className={s.subtitle}>
            Consulte o boletim e faltas do seu educando
          </p>
        </div>
      </div>

      {/* Search form */}
      <div className={s.form} style={{ marginBottom: 24 }}>
        <div
          style={{
            display: "flex",
            gap: 12,
            alignItems: "flex-end",
          }}
        >
          <div className={s.field} style={{ flex: 1 }}>
            <label className={s.label}>ID do Aluno</label>
            <input
              className={s.input}
              type="text"
              placeholder="Introduza o UUID do aluno"
              value={alunoId}
              onChange={(e) => setAlunoId(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleConsultar()}
            />
          </div>
          <button
            className={s.primaryBtn}
            onClick={handleConsultar}
            disabled={loading || !alunoId.trim()}
            style={{ display: "flex", alignItems: "center", gap: 8 }}
          >
            <Search size={16} />
            Consultar
          </button>
        </div>
      </div>

      {/* Period tabs */}
      <div className={s.tabs}>
        {[1, 2, 3].map((p) => (
          <button
            key={p}
            className={`${s.tab} ${periodo === p ? s.tabActive : ""}`}
            onClick={() => handlePeriodoChange(p)}
          >
            {p}o Periodo
          </button>
        ))}
      </div>

      {loading ? (
        <p className={s.muted}>A carregar...</p>
      ) : error ? (
        <div className={s.emptyState}>
          <div className={s.emptyIcon}>
            <AlertTriangle size={48} />
          </div>
          <p>{error}</p>
        </div>
      ) : !consulted ? (
        <div className={s.emptyState}>
          <div className={s.emptyIcon}>
            <Search size={48} />
          </div>
          <p>Introduza o ID do aluno para consultar os dados.</p>
        </div>
      ) : (
        <>
          {/* Faltas resumo */}
          {resumo && (
            <div className={s.section}>
              <h2 className={s.sectionTitle}>Resumo de Faltas</h2>
              <div className={s.statsGrid}>
                <div className={s.statCard}>
                  <div
                    className={s.statIcon}
                    style={{ background: "#1A3F7A20", color: "#1A3F7A" }}
                  >
                    <FileText size={24} />
                  </div>
                  <div>
                    <div className={s.statValue}>{resumo.total}</div>
                    <div className={s.statLabel}>Total</div>
                  </div>
                </div>
                <div className={s.statCard}>
                  <div
                    className={s.statIcon}
                    style={{ background: "#00A87820", color: "#00A878" }}
                  >
                    <FileText size={24} />
                  </div>
                  <div>
                    <div className={s.statValue}>{resumo.justificadas}</div>
                    <div className={s.statLabel}>Justificadas</div>
                  </div>
                </div>
                <div className={s.statCard}>
                  <div
                    className={s.statIcon}
                    style={{ background: "#E53E3E20", color: "#E53E3E" }}
                  >
                    <AlertTriangle size={24} />
                  </div>
                  <div>
                    <div className={s.statValue}>{resumo.injustificadas}</div>
                    <div className={s.statLabel}>Injustificadas</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Boletim table */}
          <div className={s.section}>
            <h2 className={s.sectionTitle}>
              Boletim - {periodo}o Periodo
            </h2>
            {!boletim || boletim.disciplinas.length === 0 ? (
              <div className={s.emptyState}>
                <p>Sem dados de boletim para o {periodo}o periodo.</p>
              </div>
            ) : (
              <div className={s.table}>
                <table>
                  <thead>
                    <tr>
                      <th>Disciplina</th>
                      <th>Media</th>
                      <th>Faltas</th>
                    </tr>
                  </thead>
                  <tbody>
                    {boletim.disciplinas.map((disc) => (
                      <tr key={disc.disciplina_id}>
                        <td>
                          <span className={s.nameCell}>
                            {disc.disciplina_nome}
                          </span>
                        </td>
                        <td>
                          {disc.media !== null ? (
                            <span
                              className={`${s.badge} ${
                                disc.media >= 10
                                  ? s.badgeGreen
                                  : s.badgeRed
                              }`}
                            >
                              {disc.media.toFixed(1)}
                            </span>
                          ) : (
                            <span className={`${s.badge} ${s.badgeGray}`}>
                              --
                            </span>
                          )}
                        </td>
                        <td>{disc.faltas_total}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
