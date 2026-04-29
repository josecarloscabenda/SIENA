import { useEffect, useState } from "react";
import { FileText, Award } from "lucide-react";
import api from "@/shared/api/client";
import type { BoletimResponse } from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

export default function Boletim() {
  const { user } = useAuth();
  const [periodo, setPeriodo] = useState(1);
  const [boletim, setBoletim] = useState<BoletimResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const alunoId = user?.aluno_id;

  useEffect(() => {
    if (!alunoId) {
      setLoading(false);
      setError("O seu perfil de aluno ainda não está associado.");
      return;
    }

    setLoading(true);
    setError("");

    api
      .get<BoletimResponse>(`/alunos/${alunoId}/boletim?periodo=${periodo}`)
      .then((res) => setBoletim(res.data))
      .catch(() => {
        setBoletim(null);
        setError("Não foi possível carregar o boletim.");
      })
      .finally(() => setLoading(false));
  }, [alunoId, periodo]);

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>Boletim</h1>
          <p className={s.subtitle}>Consulte as suas notas por periodo</p>
        </div>
      </div>

      {/* Period tabs */}
      <div className={s.tabs}>
        {[1, 2, 3].map((p) => (
          <button
            key={p}
            className={`${s.tab} ${periodo === p ? s.tabActive : ""}`}
            onClick={() => setPeriodo(p)}
          >
            {p}.º Período
          </button>
        ))}
      </div>

      {loading ? (
        <p className={s.muted}>A carregar...</p>
      ) : error ? (
        <div className={s.emptyState}>
          <div className={s.emptyIcon}>
            <FileText size={48} />
          </div>
          <p>{error}</p>
        </div>
      ) : !boletim || boletim.disciplinas.length === 0 ? (
        <div className={s.emptyState}>
          <div className={s.emptyIcon}>
            <FileText size={48} />
          </div>
          <p>Sem dados de boletim para o {periodo}.º período.</p>
        </div>
      ) : (
        <>
          <div className={s.table}>
            <table>
              <thead>
                <tr>
                  <th>Disciplina</th>
                  <th>Média</th>
                  <th>Faltas</th>
                </tr>
              </thead>
              <tbody>
                {boletim.disciplinas.map((disc) => {
                  const m = disc.media !== null ? Number(disc.media) : null;
                  return (
                    <tr key={disc.disciplina_id}>
                      <td>
                        <span className={s.nameCell}>{disc.disciplina_nome}</span>
                      </td>
                      <td>
                        {m !== null ? (
                          <span
                            className={`${s.badge} ${
                              m >= 10 ? s.badgeGreen : s.badgeRed
                            }`}
                          >
                            {m.toFixed(2)}
                          </span>
                        ) : (
                          <span className={`${s.badge} ${s.badgeGray}`}>—</span>
                        )}
                      </td>
                      <td>{disc.faltas_total}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Resumo médio do período */}
          {(() => {
            const validas = boletim.disciplinas
              .map((d) => (d.media !== null ? Number(d.media) : null))
              .filter((m): m is number => m !== null);
            if (validas.length === 0) return null;
            const mediaPeriodo =
              validas.reduce((a, b) => a + b, 0) / validas.length;
            return (
              <div className={s.section} style={{ marginTop: 16 }}>
                <p style={{ fontSize: "1rem" }}>
                  <Award
                    size={18}
                    style={{ verticalAlign: "middle", marginRight: 8, color: "#1A3F7A" }}
                  />
                  Média do período:{" "}
                  <strong
                    className={`${s.badge} ${
                      mediaPeriodo >= 10 ? s.badgeGreen : s.badgeRed
                    }`}
                  >
                    {mediaPeriodo.toFixed(2)}
                  </strong>
                </p>
              </div>
            );
          })()}
        </>
      )}
    </div>
  );
}
