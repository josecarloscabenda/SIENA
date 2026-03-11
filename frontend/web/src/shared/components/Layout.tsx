import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  BookOpen,
  GraduationCap,
  Home,
  LogOut,
  School,
  Users,
} from "lucide-react";
import { useAuth } from "@/shared/hooks/useAuth";
import styles from "./Layout.module.css";

const navItems = [
  { to: "/", icon: Home, label: "Dashboard" },
  { to: "/escolas", icon: School, label: "Escolas" },
  { to: "/users", icon: Users, label: "Utilizadores", roles: ["super_admin", "diretor"] },
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
      secretaria: "Secretária",
      aluno: "Aluno",
    };
    return papeis.map((p) => map[p] || p).join(", ");
  };

  return (
    <div className={styles.container}>
      {/* Sidebar */}
      <aside className={styles.sidebar}>
        <div className={styles.brand}>
          <GraduationCap size={28} />
          <div>
            <div className={styles.brandTitle}>SIENA</div>
            <div className={styles.brandSub}>Educação Angola</div>
          </div>
        </div>

        <nav className={styles.nav}>
          {navItems
            .filter((item) => !item.roles || hasRole(...item.roles))
            .map((item) => (
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

      {/* Main content */}
      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  );
}