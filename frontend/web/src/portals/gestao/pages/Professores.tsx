import { useEffect, useState } from "react";
import { Plus, Search, GraduationCap } from "lucide-react";
import api from "@/shared/api/client";
import type { ProfessorResponse, PaginatedResponse } from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

interface ProfessorForm {
  nome_completo: string;
  bi_identificacao: string;
  dt_nascimento: string;
  sexo: string;
  nacionalidade: string;
  telefone: string;
  email: string;
  codigo_funcional: string;
  especialidade: string;
  carga_horaria_semanal: number;
  tipo_contrato: string;
  nivel_academico: string;
}

const emptyForm: ProfessorForm = {
  nome_completo: "",
  bi_identificacao: "",
  dt_nascimento: "",
  sexo: "M",
  nacionalidade: "Angolana",
  telefone: "",
  email: "",
  codigo_funcional: "",
  especialidade: "",
  carga_horaria_semanal: 20,
  tipo_contrato: "efetivo",
  nivel_academico: "",
};

const contratoLabel: Record<string, string> = {
  efetivo: "Efetivo",
  contrato: "Contrato",
  substituto: "Substituto",
};

export default function Professores() {
  const { hasRole } = useAuth();
  const [professores, setProfessores] = useState<ProfessorResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<ProfessorForm>(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const canManage = hasRole("super_admin", "diretor");

  const fetchProfessores = () => {
    setLoading(true);
    const params = new URLSearchParams({ offset: "0", limit: "50" });
    if (search) params.set("search", search);
    api
      .get<PaginatedResponse<ProfessorResponse>>(`/professores?${params}`)
      .then(({ data }) => {
        setProfessores(data.items);
        setTotal(data.total);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchProfessores();
  }, [search]);

  const openEdit = (prof: ProfessorResponse) => {
    setEditingId(prof.id);
    setForm({
      nome_completo: prof.pessoa.nome_completo,
      bi_identificacao: prof.pessoa.bi_identificacao,
      dt_nascimento: prof.pessoa.dt_nascimento,
      sexo: prof.pessoa.sexo,
      nacionalidade: prof.pessoa.nacionalidade,
      telefone: prof.pessoa.telefone || "",
      email: prof.pessoa.email || "",
      codigo_funcional: prof.codigo_funcional,
      especialidade: prof.especialidade,
      carga_horaria_semanal: prof.carga_horaria_semanal,
      tipo_contrato: prof.tipo_contrato,
      nivel_academico: prof.nivel_academico || "",
    });
    setShowForm(true);
    setError("");
  };

  const openCreate = () => {
    setEditingId(null);
    setForm(emptyForm);
    setShowForm(true);
    setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      if (editingId) {
        await api.patch(`/professores/${editingId}`, form);
      } else {
        await api.post("/professores", form);
      }
      setShowForm(false);
      setEditingId(null);
      fetchProfessores();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao guardar professor.");
    } finally {
      setSaving(false);
    }
  };

  const filtered = professores.filter((p) => {
    const q = search.toLowerCase();
    return (
      p.pessoa.nome_completo.toLowerCase().includes(q) ||
      p.pessoa.bi_identificacao.toLowerCase().includes(q) ||
      p.codigo_funcional.toLowerCase().includes(q)
    );
  });

  if (showForm) {
    return (
      <div>
        <button className={s.backBtn} onClick={() => { setShowForm(false); setEditingId(null); }}>
          &larr; Voltar
        </button>
        <h1 className={s.pageTitle}>{editingId ? "Editar Professor" : "Novo Professor"}</h1>

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
              <label className={s.label}>Codigo Funcional</label>
              <input className={s.input} required value={form.codigo_funcional} onChange={(e) => setForm({ ...form, codigo_funcional: e.target.value })} />
            </div>
            <div className={s.field}>
              <label className={s.label}>Especialidade</label>
              <input className={s.input} required value={form.especialidade} onChange={(e) => setForm({ ...form, especialidade: e.target.value })} />
            </div>
            <div className={s.field}>
              <label className={s.label}>Carga Horaria Semanal</label>
              <input className={s.input} type="number" required value={form.carga_horaria_semanal} onChange={(e) => setForm({ ...form, carga_horaria_semanal: Number(e.target.value) })} />
            </div>
            <div className={s.field}>
              <label className={s.label}>Tipo de Contrato</label>
              <select className={s.input} value={form.tipo_contrato} onChange={(e) => setForm({ ...form, tipo_contrato: e.target.value })}>
                <option value="efetivo">Efetivo</option>
                <option value="contrato">Contrato</option>
                <option value="substituto">Substituto</option>
              </select>
            </div>
            <div className={s.field}>
              <label className={s.label}>Nivel Academico</label>
              <input className={s.input} value={form.nivel_academico} onChange={(e) => setForm({ ...form, nivel_academico: e.target.value })} />
            </div>
          </div>
          <div className={s.formActions}>
            <button type="button" className={s.cancelBtn} onClick={() => { setShowForm(false); setEditingId(null); }}>Cancelar</button>
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
          <h1 className={s.pageTitle}>Professores</h1>
          <p className={s.subtitle}>{total} professor(es) registado(s)</p>
        </div>
        {canManage && (
          <button className={s.addBtn} onClick={openCreate}>
            <Plus size={18} />
            Novo Professor
          </button>
        )}
      </div>

      <div className={s.searchBar}>
        <Search size={18} color="var(--text-muted)" />
        <input
          type="text"
          placeholder="Pesquisar por nome, BI ou codigo funcional..."
          className={s.searchInput}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <p className={s.muted}>A carregar...</p>
      ) : filtered.length === 0 ? (
        <p className={s.muted}>Nenhum professor encontrado.</p>
      ) : (
        <div className={s.table}>
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>BI</th>
                <th>Codigo Funcional</th>
                <th>Especialidade</th>
                <th>Contrato</th>
                {canManage && <th>Accoes</th>}
              </tr>
            </thead>
            <tbody>
              {filtered.map((prof) => (
                <tr key={prof.id}>
                  <td>
                    <div className={s.nameCell}>
                      <GraduationCap size={16} />
                      {prof.pessoa.nome_completo}
                    </div>
                  </td>
                  <td>{prof.pessoa.bi_identificacao}</td>
                  <td>{prof.codigo_funcional}</td>
                  <td>{prof.especialidade}</td>
                  <td>{contratoLabel[prof.tipo_contrato] || prof.tipo_contrato}</td>
                  {canManage && (
                    <td>
                      <button className={s.editBtn} onClick={() => openEdit(prof)}>
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
