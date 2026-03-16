import { ShieldX } from "lucide-react";
import { useNavigate } from "react-router-dom";
import styles from "./Forbidden.module.css";

export default function Forbidden() {
  const navigate = useNavigate();

  return (
    <div className={styles.container}>
      <ShieldX size={64} color="var(--danger)" />
      <h1 className={styles.title}>Acesso Negado</h1>
      <p className={styles.message}>
        Nao tem permissao para aceder a esta pagina.
      </p>
      <button className={styles.btn} onClick={() => navigate("/")}>
        Voltar ao Dashboard
      </button>
    </div>
  );
}
