import { useEffect, useMemo, useState, type FormEvent } from "react";
import { Navigate, useParams, useSearchParams } from "react-router-dom";
import { GraduationCap, School } from "lucide-react";
import api from "@/shared/api/client";
import { useAuth } from "@/shared/hooks/useAuth";
import type { TenantPublicResponse } from "@/shared/api/types";
import styles from "./Login.module.css";

export default function Login() {
  const { login, isAuthenticated, loading } = useAuth();
  const params = useParams<{ slug?: string }>();
  const [searchParams] = useSearchParams();

  const [tenants, setTenants] = useState<TenantPublicResponse[]>([]);
  const [loadingTenants, setLoadingTenants] = useState(true);
  const [selectedSlug, setSelectedSlug] = useState<string>("");
  const [lockedSlug, setLockedSlug] = useState<string | null>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  /* Resolve slug from URL path (/escola/:slug/login) or query (?escola=slug) */
  const urlSlug = useMemo(() => {
    return params.slug || searchParams.get("escola") || null;
  }, [params.slug, searchParams]);

  /* Load list of tenants (public endpoint) */
  useEffect(() => {
    setLoadingTenants(true);
    api
      .get<TenantPublicResponse[]>("/auth/tenants")
      .then(({ data }) => {
        setTenants(data);
        if (urlSlug) {
          const match = data.find((t) => t.slug === urlSlug);
          if (match) {
            setSelectedSlug(match.slug);
            setLockedSlug(match.slug);
          } else {
            setError(`Escola "${urlSlug}" não encontrada. Seleccione uma escola disponível.`);
          }
        } else {
          const savedSlug = localStorage.getItem("tenant_slug");
          if (savedSlug && data.some((t) => t.slug === savedSlug)) {
            setSelectedSlug(savedSlug);
          } else if (data.length === 1) {
            setSelectedSlug(data[0].slug);
          }
        }
      })
      .catch(() => {
        setError("Não foi possível carregar a lista de escolas. Tente novamente.");
      })
      .finally(() => setLoadingTenants(false));
  }, [urlSlug]);

  if (loading) return null;
  if (isAuthenticated) return <Navigate to="/" replace />;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    if (!selectedSlug) {
      setError("Seleccione uma escola.");
      return;
    }
    setSubmitting(true);

    try {
      await login(username, password, { tenantSlug: selectedSlug });
    } catch {
      setError("Credenciais inválidas. Verifique a escola, utilizador e palavra-passe.");
    } finally {
      setSubmitting(false);
    }
  };

  const selectedTenant = tenants.find((t) => t.slug === selectedSlug);

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.header}>
          <GraduationCap size={40} color="#1A3F7A" />
          <h1 className={styles.title}>SIENA</h1>
          <p className={styles.subtitle}>
            Sistema de Integração Educacional Nacional de Angola
          </p>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          {error && <div className={styles.error}>{error}</div>}

          <div className={styles.field}>
            <label htmlFor="escola" className={styles.label}>
              Escola
            </label>
            {lockedSlug && selectedTenant ? (
              <div className={styles.tenantLocked}>
                <School size={18} />
                <span>{selectedTenant.nome}</span>
              </div>
            ) : (
              <select
                id="escola"
                className={styles.input}
                value={selectedSlug}
                onChange={(e) => setSelectedSlug(e.target.value)}
                disabled={loadingTenants}
                required
              >
                <option value="">
                  {loadingTenants ? "A carregar escolas..." : "Seleccione a escola..."}
                </option>
                {tenants.map((t) => (
                  <option key={t.id} value={t.slug}>
                    {t.nome}
                  </option>
                ))}
              </select>
            )}
          </div>

          <div className={styles.field}>
            <label htmlFor="username" className={styles.label}>
              Utilizador
            </label>
            <input
              id="username"
              type="text"
              className={styles.input}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Introduza o seu utilizador"
              required
              autoFocus
            />
          </div>

          <div className={styles.field}>
            <label htmlFor="password" className={styles.label}>
              Palavra-passe
            </label>
            <input
              id="password"
              type="password"
              className={styles.input}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Introduza a sua palavra-passe"
              required
            />
          </div>

          <button
            type="submit"
            className={styles.button}
            disabled={submitting || !selectedSlug}
          >
            {submitting ? "A autenticar..." : "Entrar"}
          </button>
        </form>

        <p className={styles.footer}>Educar é transformar o futuro de Angola</p>
      </div>
    </div>
  );
}
