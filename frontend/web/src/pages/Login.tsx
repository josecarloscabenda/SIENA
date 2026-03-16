import { useState, type FormEvent } from "react";
import { Navigate } from "react-router-dom";
import { GraduationCap } from "lucide-react";
import { useAuth } from "@/shared/hooks/useAuth";
import styles from "./Login.module.css";

// Default tenant for pilot
const PILOT_TENANT_ID = "9404f9cd-8f99-4126-8e00-b227a48c3b37";

export default function Login() {
  const { login, isAuthenticated, loading } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (loading) return null;
  if (isAuthenticated) return <Navigate to="/" replace />;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      await login(username, password, PILOT_TENANT_ID);
    } catch {
      setError("Credenciais inválidas. Verifique o username e password.");
    } finally {
      setSubmitting(false);
    }
  };

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
            disabled={submitting}
          >
            {submitting ? "A autenticar..." : "Entrar"}
          </button>
        </form>

        <p className={styles.footer}>Educar é transformar o futuro de Angola</p>
      </div>
    </div>
  );
}