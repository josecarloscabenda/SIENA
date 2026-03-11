import { useEffect, useState } from "react";
import { Plus, School, Search } from "lucide-react";
import api from "@/shared/api/client";
import type { EscolaResponse, PaginatedResponse } from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import EscolaForm from "./EscolaForm";
import styles from "./Escolas.module.css";

export default function Escolas() {
  const { hasRole } = useAuth();
  const [escolas, setEscolas] = useState<EscolaResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const canManage = hasRole("super_admin", "diretor");

  const fetchEscolas = () => {
    setLoading(true);
    api
      .get<PaginatedResponse<EscolaResponse>>("/escolas?limit=50")
      .then(({ data }) => {
        setEscolas(data.items);
        setTotal(data.total);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchEscolas();
  }, []);

  const filtered = escolas.filter(
    (e) =>
      e.nome.toLowerCase().includes(search.toLowerCase()) ||
      e.provincia.toLowerCase().includes(search.toLowerCase()) ||
      e.municipio.toLowerCase().includes(search.toLowerCase()) ||
      (e.codigo_sige?.toLowerCase().includes(search.toLowerCase()) ?? false),
  );

  const tipoLabel: Record<string, string> = {
    publica: "Pública",
    privada: "Privada",
    comparticipada: "Comparticipada",
  };

  const nivelLabel: Record<string, string> = {
    primario: "Primário",
    secundario_1ciclo: "Sec. 1.º Ciclo",
    secundario_2ciclo: "Sec. 2.º Ciclo",
    tecnico: "Técnico",
  };

  if (showForm || editingId) {
    return (
      <EscolaForm
        escolaId={editingId}
        onClose={() => {
          setShowForm(false);
          setEditingId(null);
        }}
        onSaved={() => {
          setShowForm(false);
          setEditingId(null);
          fetchEscolas();
        }}
      />
    );
  }

  return (
    <div>
      <div className={styles.pageHeader}>
        <div>
          <h1 className={styles.pageTitle}>Escolas</h1>
          <p className={styles.subtitle}>{total} escola(s) registada(s)</p>
        </div>
        {canManage && (
          <button className={styles.addBtn} onClick={() => setShowForm(true)}>
            <Plus size={18} />
            Nova Escola
          </button>
        )}
      </div>

      <div className={styles.searchBar}>
        <Search size={18} color="var(--text-muted)" />
        <input
          type="text"
          placeholder="Pesquisar por nome, província, município ou código SIGE..."
          className={styles.searchInput}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <p className={styles.muted}>A carregar...</p>
      ) : filtered.length === 0 ? (
        <p className={styles.muted}>Nenhuma escola encontrada.</p>
      ) : (
        <div className={styles.table}>
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>Tipo</th>
                <th>Nível</th>
                <th>Província</th>
                <th>Município</th>
                <th>SIGE</th>
                <th>Estado</th>
                {canManage && <th>Acções</th>}
              </tr>
            </thead>
            <tbody>
              {filtered.map((escola) => (
                <tr key={escola.id}>
                  <td>
                    <div className={styles.escolaNome}>
                      <School size={16} />
                      {escola.nome}
                    </div>
                  </td>
                  <td>{tipoLabel[escola.tipo] || escola.tipo}</td>
                  <td>{nivelLabel[escola.nivel_ensino] || escola.nivel_ensino}</td>
                  <td>{escola.provincia}</td>
                  <td>{escola.municipio}</td>
                  <td className={styles.sige}>{escola.codigo_sige || "—"}</td>
                  <td>
                    <span
                      className={`${styles.badge} ${escola.ativa ? styles.badgeActive : styles.badgeInactive}`}
                    >
                      {escola.ativa ? "Ativa" : "Inativa"}
                    </span>
                  </td>
                  {canManage && (
                    <td>
                      <button
                        className={styles.editBtn}
                        onClick={() => setEditingId(escola.id)}
                      >
                        Editar
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}