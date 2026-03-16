import { useEffect, useState, type FormEvent } from "react";
import { ArrowLeft } from "lucide-react";
import api from "@/shared/api/client";
import type { EscolaDetailResponse } from "@/shared/api/types";
import styles from "./EscolaForm.module.css";

interface Props {
  escolaId: string | null;
  onClose: () => void;
  onSaved: () => void;
}

const PROVINCIAS = [
  "Bengo", "Benguela", "Bié", "Cabinda", "Cuando Cubango",
  "Cuanza Norte", "Cuanza Sul", "Cunene", "Huambo", "Huíla",
  "Luanda", "Lunda Norte", "Lunda Sul", "Malanje", "Moxico",
  "Namibe", "Uíge", "Zaire",
];

export default function EscolaForm({ escolaId, onClose, onSaved }: Props) {
  const isEditing = !!escolaId;
  const [loading, setLoading] = useState(isEditing);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const [nome, setNome] = useState("");
  const [codigoSige, setCodigoSige] = useState("");
  const [tipo, setTipo] = useState("publica");
  const [nivelEnsino, setNivelEnsino] = useState("primario");
  const [provincia, setProvincia] = useState("Luanda");
  const [municipio, setMunicipio] = useState("");
  const [comuna, setComuna] = useState("");
  const [endereco, setEndereco] = useState("");
  const [telefone, setTelefone] = useState("");
  const [email, setEmail] = useState("");

  useEffect(() => {
    if (escolaId) {
      api
        .get<EscolaDetailResponse>(`/escolas/${escolaId}`)
        .then(({ data }) => {
          setNome(data.nome);
          setCodigoSige(data.codigo_sige || "");
          setTipo(data.tipo);
          setNivelEnsino(data.nivel_ensino);
          setProvincia(data.provincia);
          setMunicipio(data.municipio);
          setComuna(data.comuna || "");
          setEndereco(data.endereco || "");
          setTelefone(data.telefone || "");
          setEmail(data.email || "");
        })
        .catch(() => setError("Erro ao carregar escola"))
        .finally(() => setLoading(false));
    }
  }, [escolaId]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);

    const payload = {
      nome,
      codigo_sige: codigoSige || null,
      tipo,
      nivel_ensino: nivelEnsino,
      provincia,
      municipio,
      comuna: comuna || null,
      endereco: endereco || null,
      telefone: telefone || null,
      email: email || null,
    };

    try {
      if (isEditing) {
        await api.patch(`/escolas/${escolaId}`, payload);
      } else {
        await api.post("/escolas", payload);
      }
      onSaved();
    } catch (err: unknown) {
      const msg =
        err && typeof err === "object" && "response" in err
          ? (err as { response: { data: { detail: string } } }).response?.data?.detail
          : null;
      setError(msg || "Erro ao guardar escola");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <p>A carregar...</p>;

  return (
    <div>
      <button className={styles.backBtn} onClick={onClose}>
        <ArrowLeft size={18} />
        Voltar à lista
      </button>

      <h1 className={styles.title}>
        {isEditing ? "Editar Escola" : "Nova Escola"}
      </h1>

      <form onSubmit={handleSubmit} className={styles.form}>
        {error && <div className={styles.error}>{error}</div>}

        <div className={styles.grid}>
          <div className={styles.field}>
            <label className={styles.label}>Nome da Escola *</label>
            <input
              className={styles.input}
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              required
              placeholder="Ex: Escola Primária Nº 1"
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Código SIGE</label>
            <input
              className={styles.input}
              value={codigoSige}
              onChange={(e) => setCodigoSige(e.target.value)}
              placeholder="Ex: SIGE-LDA-001"
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Tipo *</label>
            <select
              className={styles.input}
              value={tipo}
              onChange={(e) => setTipo(e.target.value)}
            >
              <option value="publica">Pública</option>
              <option value="privada">Privada</option>
              <option value="comparticipada">Comparticipada</option>
            </select>
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Nível de Ensino *</label>
            <select
              className={styles.input}
              value={nivelEnsino}
              onChange={(e) => setNivelEnsino(e.target.value)}
            >
              <option value="primario">Primário</option>
              <option value="secundario_1ciclo">Secundário 1.º Ciclo</option>
              <option value="secundario_2ciclo">Secundário 2.º Ciclo</option>
              <option value="tecnico">Técnico</option>
            </select>
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Província *</label>
            <select
              className={styles.input}
              value={provincia}
              onChange={(e) => setProvincia(e.target.value)}
            >
              {PROVINCIAS.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Município *</label>
            <input
              className={styles.input}
              value={municipio}
              onChange={(e) => setMunicipio(e.target.value)}
              required
              placeholder="Ex: Viana"
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Comuna</label>
            <input
              className={styles.input}
              value={comuna}
              onChange={(e) => setComuna(e.target.value)}
              placeholder="Ex: Ingombota"
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Telefone</label>
            <input
              className={styles.input}
              value={telefone}
              onChange={(e) => setTelefone(e.target.value)}
              placeholder="+244 222 123 456"
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Email</label>
            <input
              className={styles.input}
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="escola@med.gov.ao"
            />
          </div>

          <div className={styles.fieldFull}>
            <label className={styles.label}>Endereço</label>
            <input
              className={styles.input}
              value={endereco}
              onChange={(e) => setEndereco(e.target.value)}
              placeholder="Rua, Bairro, Cidade"
            />
          </div>
        </div>

        <div className={styles.actions}>
          <button
            type="button"
            className={styles.cancelBtn}
            onClick={onClose}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className={styles.submitBtn}
            disabled={submitting}
          >
            {submitting
              ? "A guardar..."
              : isEditing
                ? "Guardar Alterações"
                : "Criar Escola"}
          </button>
        </div>
      </form>
    </div>
  );
}