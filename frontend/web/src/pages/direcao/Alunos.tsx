import { useEffect, useState } from "react";
import { Plus, Search, Users } from "lucide-react";
import api from "@/shared/api/client";
import type { AlunoResponse, PaginatedResponse } from "@/shared/api/types";
import { useAuth } from "@/shared/hooks/useAuth";
import s from "@/shared/styles/common.module.css";

interface AlunoForm {
  nome_completo: string;
  bi_identificacao: string;
  dt_nascimento: string;
  sexo: string;
  nacionalidade: string;
  morada: string;
  telefone: string;
  email: string;
  n_processo: string;
  ano_ingresso: number;
  necessidades_especiais: boolean;
  status: string;
}

const emptyForm: AlunoForm = {
  nome_completo: "",
  bi_identificacao: "",
  dt_nascimento: "",
  sexo: "M",
  nacionalidade: "Angolana",
  morada: "",
  telefone: "",
  email: "",
  n_processo: "",
  ano_ingresso: new Date().getFullYear(),
  necessidades_especiais: false,
  status: "ativo",
};

const statusBadge: Record<string, string> = {
  ativo: s.badgeGreen,
  transferido: s.badgeBlue,
  desistente: s.badgeRed,
  concluinte: s.badgeYellow,
};

const statusLabel: Record<string, string> = {
  ativo: "Ativo",
  transferido: "Transferido",
  desistente: "Desistente",
  concluinte: "Concluinte",
};

export default function Alunos() {
  const { hasRole } = useAuth();
  const [alunos, setAlunos] = useState<AlunoResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<AlunoForm>(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const canManage = hasRole("super_admin", "diretor", "secretaria");

  const fetchAlunos = () => {
    setLoading(true);
    const params = new URLSearchParams({ offset: "0", limit: "50" });
    if (search) params.set("search", search);
    api
      .get<PaginatedResponse<AlunoResponse>>(`/alunos?${params}`)
      .then(({ data }) => {
        setAlunos(data.items);
        setTotal(data.total);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAlunos();
  }, [search]);

  const openEdit = (aluno: AlunoResponse) => {
    setEditingId(aluno.id);
    setForm({
      nome_completo: aluno.pessoa.nome_completo,
      bi_identificacao: aluno.pessoa.bi_identificacao,
      dt_nascimento: aluno.pessoa.dt_nascimento,
      sexo: aluno.pessoa.sexo,
      nacionalidade: aluno.pessoa.nacionalidade,
      morada: aluno.pessoa.morada || "",
      telefone: aluno.pessoa.telefone || "",
      email: aluno.pessoa.email || "",
      n_processo: aluno.n_processo,
      ano_ingresso: aluno.ano_ingresso,
      necessidades_especiais: aluno.necessidades_especiais,
      status: aluno.status,
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
        await api.patch(`/alunos/${editingId}`, form);
      } else {
        await api.post("/alunos", form);
      }
      setShowForm(false);
      setEditingId(null);
      fetchAlunos();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao guardar aluno.");
    } finally {
      setSaving(false);
    }
  };

  const filtered = alunos.filter((a) => {
    const q = search.toLowerCase();
    return (
      a.pessoa.nome_completo.toLowerCase().includes(q) ||
      a.pessoa.bi_identificacao.toLowerCase().includes(q) ||
      a.n_processo.toLowerCase().includes(q)
    );
  });

  if (showForm) {
    return (
      <div>
        <button className={s.backBtn} onClick={() => { setShowForm(false); setEditingId(null); }}>
          &larr; Voltar
        </button>
        <h1 className={s.pageTitle}>{editingId ? "Editar Aluno" : "Novo Aluno"}</h1>

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
              <label className={s.label}>Morada</label>
              <input className={s.input} value={form.morada} onChange={(e) => setForm({ ...form, morada: e.target.value })} />
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
              <label className={s.label}>N.o Processo</label>
              <input className={s.input} required value={form.n_processo} onChange={(e) => setForm({ ...form, n_processo: e.target.value })} />
            </div>
            <div className={s.field}>
              <label className={s.label}>Ano de Ingresso</label>
              <input className={s.input} type="number" required value={form.ano_ingresso} onChange={(e) => setForm({ ...form, ano_ingresso: Number(e.target.value) })} />
            </div>
            <div className={s.field}>
              <label className={s.label}>Status</label>
              <select className={s.input} value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
                <option value="ativo">Ativo</option>
                <option value="transferido">Transferido</option>
                <option value="desistente">Desistente</option>
                <option value="concluinte">Concluinte</option>
              </select>
            </div>
            <div className={s.field} style={{ justifyContent: "center" }}>
              <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: "0.85rem" }}>
                <input type="checkbox" checked={form.necessidades_especiais} onChange={(e) => setForm({ ...form, necessidades_especiais: e.target.checked })} />
                Necessidades Especiais
              </label>
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
          <h1 className={s.pageTitle}>Alunos</h1>
          <p className={s.subtitle}>{total} aluno(s) registado(s)</p>
        </div>
        {canManage && (
          <button className={s.addBtn} onClick={openCreate}>
            <Plus size={18} />
            Novo Aluno
          </button>
        )}
      </div>

      <div className={s.searchBar}>
        <Search size={18} color="var(--text-muted)" />
        <input
          type="text"
          placeholder="Pesquisar por nome, BI ou n.o processo..."
          className={s.searchInput}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <p className={s.muted}>A carregar...</p>
      ) : filtered.length === 0 ? (
        <p className={s.muted}>Nenhum aluno encontrado.</p>
      ) : (
        <div className={s.table}>
          <table>
            <thead>
              <tr>
                <th>Nome</th>
                <th>BI</th>
                <th>N.o Processo</th>
                <th>Sexo</th>
                <th>Status</th>
                {canManage && <th>Accoes</th>}
              </tr>
            </thead>
            <tbody>
              {filtered.map((aluno) => (
                <tr key={aluno.id}>
                  <td>
                    <div className={s.nameCell}>
                      <Users size={16} />
                      {aluno.pessoa.nome_completo}
                    </div>
                  </td>
                  <td>{aluno.pessoa.bi_identificacao}</td>
                  <td>{aluno.n_processo}</td>
                  <td>{aluno.pessoa.sexo === "M" ? "Masculino" : "Feminino"}</td>
                  <td>
                    <span className={`${s.badge} ${statusBadge[aluno.status] || s.badgeGray}`}>
                      {statusLabel[aluno.status] || aluno.status}
                    </span>
                  </td>
                  {canManage && (
                    <td>
                      <button className={s.editBtn} onClick={() => openEdit(aluno)}>
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
