import { useEffect, useState } from "react";
import { Plus, Search, UserCheck } from "lucide-react";
import api from "@/shared/api/client";
import type { EncarregadoResponse, PaginatedResponse } from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

interface EncarregadoForm {
  nome_completo: string;
  bi_identificacao: string;
  dt_nascimento: string;
  sexo: string;
  nacionalidade: string;
  telefone: string;
  email: string;
  profissao: string;
  escolaridade: string;
}

const emptyForm: EncarregadoForm = {
  nome_completo: "",
  bi_identificacao: "",
  dt_nascimento: "",
  sexo: "M",
  nacionalidade: "Angolana",
  telefone: "",
  email: "",
  profissao: "",
  escolaridade: "",
};

export default function Encarregados() {
  const { hasRole } = useAuth();
  const [encarregados, setEncarregados] = useState<EncarregadoResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<EncarregadoForm>(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const canManage = hasRole("super_admin", "diretor", "secretaria");

  const fetchEncarregados = () => {
    setLoading(true);
    const params = new URLSearchParams({ offset: "0", limit: "50" });
    if (search) params.set("search", search);
    api
      .get<PaginatedResponse<EncarregadoResponse>>(`/encarregados?${params}`)
      .then(({ data }) => {
        setEncarregados(data.items);
        setTotal(data.total);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchEncarregados();
  }, [search]);

  const openCreate = () => {
    setForm(emptyForm);
    setShowForm(true);
    setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      await api.post("/encarregados", form);
      setShowForm(false);
      fetchEncarregados();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao guardar encarregado.");
    } finally {
      setSaving(false);
    }
  };

  const filtered = encarregados.filter((enc) => {
    const q = search.toLowerCase();
    return (
      enc.pessoa.nome_completo.toLowerCase().includes(q) ||
      enc.pessoa.bi_identificacao.toLowerCase().includes(q)
    );
  });

  if (showForm) {
    return (
      <div>
        <button className={s.backBtn} onClick={() => setShowForm(false)}>
          &larr; Voltar
        </button>
        <h1 className={s.pageTitle}>Novo Encarregado</h1>

        {error && <div className={s.error}>{error}</div>}

        <form className={s.form} onSubmit={handleSubmit}>
          <div className={s.formGrid}>
            <div className={s.field}>
              <label className={s.label}>Nome Completo</label>
              <input className={s.input} required value={form.nome_completo} onChange={(e) => setForm({ ...form, nome_completo: e.target.value })} />
            </div>
            <div className={s.field}>
              <label className={s.label}>BI / Identificacao</label>
              <input className={s.input} required value={form.bi_identificacao} onChange={(e) => setForm({ ...form, bi_identificacao: e.target.value })} />
            </div>
            <div className={s.field}>
              <label className={s.label}>Data de Nascimento</label>
              <input className={s.input} type="date" required value={form.dt_nascimento} onChange={(e) => setForm({ ...form, dt_nascimento: e.target.value })} />
            </div>
            <div className={s.field}>
              <label className={s.label}>Sexo</label>
              <select className={s.input} value={form.sexo} onChange={(e) => setForm({ ...form, sexo: e.target.value })}>
                <option value="M">Masculino</option>
                <option value="F">Feminino</option>
              </select>
            </div>
            <div className={s.field}>
              <label className={s.label}>Nacionalidade</label>
              <input className={s.input} required value={form.nacionalidade} onChange={(e) => setForm({ ...form, nacionalidade: e.target.value })} />
            </div>
            <div className={s.field}>
              <label className={s.label}>Telefone</label>
              <input className={s.input} value={form.telefone} onChange={(e) => setForm({ ...form, telefone: e.target.value })} />
            </div>
            <div className={s.field}>
              <label className={s.label}>Email</label>
              <input className={s.input} type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            </div>
            <div className={s.field}>
              <label className={s.label}>Profissao</label>
              <input className={s.input} value={form.profissao} onChange={(e) => setForm({ ...form, profissao: e.target.value })} />
            </div>
            <div className={s.field}>
              <label className={s.label}>Escolaridade</label>
              <input className={s.input} value={form.escolaridade} onChange={(e) => setForm({ ...form, escolaridade: e.target.value })} />
            </div>
          </div>
          <div className={s.formActions}>
            <button type="button" className={s.cancelBtn} onClick={() => setShowForm(false)}>Cancelar</button>
            <button type="submit" className={s.primaryBtn} disabled={saving}>{saving ? "A guardar..." : "Guardar"}</button>
          </div>
        </form>
      </div>
    );
  }

  return (
    <div>
      <div className={s.pageHeader}>
        <div>
          <h1 className={s.pageTitle}>Encarregados</h1>
          <p className={s.subtitle}>{total} encarregado(s) registado(s)</p>
        </div>
        {canManage && (
          <button className={s.addBtn} onClick={openCreate}>
            <Plus size={18} />
            Novo Encarregado
          </button>
        )}
      </div>

      <div className={s.searchBar}>
        <Search size={18} color="var(--text-muted)" />
        <input
          type="text"
          placeholder="Pesquisar por nome ou BI..."
          className={s.searchInput}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <p className={s.muted}>A carregar...</p>
      ) : filtered.length === 0 ? (
        <p className={s.muted}>Nenhum encarregado encontrado.</p>
      ) : (
        <div className={s.table}>
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>BI</th>
                <th>Profissao</th>
                <th>Escolaridade</th>
                <th>Telefone</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((enc) => (
                <tr key={enc.id}>
                  <td>
                    <div className={s.nameCell}>
                      <UserCheck size={16} />
                      {enc.pessoa.nome_completo}
                    </div>
                  </td>
                  <td>{enc.pessoa.bi_identificacao}</td>
                  <td>{enc.profissao || "—"}</td>
                  <td>{enc.escolaridade || "—"}</td>
                  <td>{enc.pessoa.telefone || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
