import { useEffect, useState } from "react";
import { FileText } from "lucide-react";
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

  useEffect(() => {
    if (!user?.id) return;

    setLoading(true);
    setError("");

    api
      .get<BoletimResponse>(`/alunos/${user.id}/boletim?periodo=${periodo}`)
      .then((res) => setBoletim(res.data))
      .catch(() => {
        setBoletim(null);
        setError("Nao foi possivel carregar o boletim. O seu perfil podera ainda nao estar associado.");
      })
      .finally(() => setLoading(false));
  }, [user?.id, periodo]);

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
            {p}o Periodo
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
                    <span className={s.nameCell}>{disc.disciplina_nome}</span>
                  </td>
                  <td>
                    {disc.media !== null ? (
                      <span
                        className={`${s.badge} ${
                          disc.media >= 10 ? s.badgeGreen : s.badgeRed
                        }`}
                      >
                        {disc.media.toFixed(1)}
                      </span>
                    ) : (
                      <span className={`${s.badge} ${s.badgeGray}`}>--</span>
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
  );
}
