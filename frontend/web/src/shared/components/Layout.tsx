import { NavLink, Outlet, useNavigate } from "react-router-dom";
import type { LucideIcon } from "lucide-react";
import {
  BookOpen,
  Calendar,
  ClipboardList,
  FileText,
  GraduationCap,
  Home,
  LayoutGrid,
  LogOut,
  School,
  UserCheck,
  Users,
  Users2,
} from "lucide-react";
import { useAuth } from "@/shared/hooks/useAuth";
import styles from "./Layout.module.css";

interface NavItem {
  to: string;
  icon: LucideIcon;
  label: string;
  roles?: string[];
}

interface NavSection {
  title?: string;
  items: NavItem[];
}

const navSections: NavSection[] = [
  {
    items: [
      { to: "/", icon: Home, label: "Dashboard" },
    ],
  },
  {
    title: "Gestao",
    items: [
      { to: "/escolas", icon: School, label: "Escolas", roles: ["super_admin", "diretor", "secretaria"] },
      { to: "/alunos", icon: Users, label: "Alunos", roles: ["super_admin", "diretor", "secretaria"] },
      { to: "/professores", icon: Users2, label: "Professores", roles: ["super_admin", "diretor"] },
      { to: "/encarregados", icon: UserCheck, label: "Encarregados", roles: ["super_admin", "diretor", "secretaria"] },
      { to: "/matriculas", icon: FileText, label: "Matriculas", roles: ["super_admin", "diretor", "secretaria"] },
      { to: "/turmas", icon: LayoutGrid, label: "Turmas", roles: ["super_admin", "diretor", "secretaria"] },
      { to: "/curriculos", icon: BookOpen, label: "Curriculos", roles: ["super_admin", "diretor"] },
      { to: "/horarios", icon: Calendar, label: "Horarios", roles: ["super_admin", "diretor", "secretaria"] },
      { to: "/pauta", icon: ClipboardList, label: "Pauta", roles: ["super_admin", "diretor", "secretaria"] },
      { to: "/users", icon: Users, label: "Utilizadores", roles: ["super_admin", "diretor"] },
    ],
  },
  {
    title: "Professor",
    items: [
      { to: "/professor/turmas", icon: LayoutGrid, label: "Minhas Turmas", roles: ["professor"] },
      { to: "/professor/diario", icon: ClipboardList, label: "Diario de Classe", roles: ["professor"] },
      { to: "/professor/notas", icon: FileText, label: "Lancar Notas", roles: ["professor"] },
      { to: "/professor/horario", icon: Calendar, label: "Meu Horario", roles: ["professor"] },
    ],
  },
  {
    title: "Aluno",
    items: [
      { to: "/aluno/boletim", icon: FileText, label: "Boletim", roles: ["aluno"] },
      { to: "/aluno/faltas", icon: ClipboardList, label: "Minhas Faltas", roles: ["aluno"] },
      { to: "/aluno/horario", icon: Calendar, label: "Meu Horario", roles: ["aluno"] },
    ],
  },
  {
    title: "Encarregado",
    items: [
      { to: "/encarregado/filhos", icon: Users, label: "Meus Educandos", roles: ["encarregado"] },
    ],
  },
];

export default function Layout() {
  const { user, logout, hasRole } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const roleLabel = (papeis: string[]) => {
    const map: Record<string, string> = {
      super_admin: "Administrador",
      diretor: "Diretor",
      professor: "Professor",
      secretaria: "Secretaria",
      aluno: "Aluno",
      encarregado: "Encarregado",
    };
    return papeis.map((p) => map[p] || p).join(", ");
  };

  return (
    <div className={styles.container}>
      <aside className={styles.sidebar}>
        <div className={styles.brand}>
          <GraduationCap size={28} />
          <div>
            <div className={styles.brandTitle}>SIENA</div>
            <div className={styles.brandSub}>Educacao Angola</div>
          </div>
        </div>

        <nav className={styles.nav}>
          {navSections.map((section, si) => {
            const visible = section.items.filter(
              (item) => !item.roles || hasRole(...item.roles),
            );
            if (visible.length === 0) return null;

            return (
              <div key={si}>
                {section.title && (
                  <div className={styles.navSection}>{section.title}</div>
                )}
                {visible.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.to === "/"}
                    className={({ isActive }) =>
                      `${styles.navLink} ${isActive ? styles.navLinkActive : ""}`
                    }
                  >
                    <item.icon size={20} />
                    {item.label}
                  </NavLink>
                ))}
              </div>
            );
          })}
        </nav>

        <div className={styles.sidebarFooter}>
          <div className={styles.userInfo}>
            <BookOpen size={16} />
            <div>
              <div className={styles.userName}>{user?.nome_completo}</div>
              <div className={styles.userRole}>
                {user?.papeis ? roleLabel(user.papeis) : ""}
              </div>
            </div>
          </div>
          <button className={styles.logoutBtn} onClick={handleLogout} title="Sair">
            <LogOut size={18} />
          </button>
        </div>
      </aside>

      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  );
}
