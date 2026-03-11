import { useEffect, useState } from "react";
import { Users as UsersIcon } from "lucide-react";
import api from "@/shared/api/client";
import type { PaginatedResponse, UserResponse } from "@/shared/api/types";
import styles from "./Users.module.css";

export default function UsersPage() {
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<PaginatedResponse<UserResponse>>("/users?limit=50")
      .then(({ data }) => {
        setUsers(data.items);
        setTotal(data.total);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const roleLabel: Record<string, string> = {
    super_admin: "Administrador",
    diretor: "Diretor",
    professor: "Professor",
    secretaria: "Secretária",
    aluno: "Aluno",
    encarregado: "Encarregado",
    gestor_municipal: "Gestor Municipal",
    gestor_provincial: "Gestor Provincial",
    gestor_nacional: "Gestor Nacional",
    platform_admin: "Admin Plataforma",
  };

  return (
    <div>
      <div className={styles.pageHeader}>
        <h1 className={styles.pageTitle}>Utilizadores</h1>
        <p className={styles.subtitle}>{total} utilizador(es)</p>
      </div>

      {loading ? (
        <p className={styles.muted}>A carregar...</p>
      ) : (
        <div className={styles.table}>
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>Username</th>
                <th>Email</th>
                <th>Papéis</th>
                <th>Estado</th>
                <th>Último Login</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td>
                    <div className={styles.userName}>
                      <UsersIcon size={16} />
                      {user.nome_completo}
                    </div>
                  </td>
                  <td className={styles.mono}>{user.username}</td>
                  <td>{user.email || "—"}</td>
                  <td>
                    <div className={styles.roles}>
                      {user.papeis.map((p) => (
                        <span key={p} className={styles.roleBadge}>
                          {roleLabel[p] || p}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td>
                    <span
                      className={`${styles.badge} ${user.ativo ? styles.badgeActive : styles.badgeInactive}`}
                    >
                      {user.ativo ? "Ativo" : "Inativo"}
                    </span>
                  </td>
                  <td className={styles.muted}>
                    {user.ultimo_login
                      ? new Date(user.ultimo_login).toLocaleDateString("pt-AO")
                      : "Nunca"}
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