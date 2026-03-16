import { NavLink, Outlet, useNavigate } from "react-router-dom";
import type { LucideIcon } from "lucide-react";
import { BookOpen, GraduationCap, LogOut } from "lucide-react";
import { useAuth } from "@/shared/hooks/useAuth";
import styles from "./PortalLayout.module.css";

export interface NavItem {
  to: string;
  icon: LucideIcon;
  label: string;
}

export interface NavSection {
  title?: string;
  items: NavItem[];
}

export interface PortalConfig {
  portalName: string;
  sidebarColor: string;
  accentColor: string;
  navSections: NavSection[];
  basePath: string;
}

export default function PortalLayout({ config }: { config: PortalConfig }) {
  const { user, logout } = useAuth();
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
      <aside
        className={styles.sidebar}
        style={{ background: config.sidebarColor }}
      >
        <div className={styles.brand}>
          <GraduationCap size={28} />
          <div>
            <div className={styles.brandTitle}>SIENA</div>
            <div className={styles.brandSub}>{config.portalName}</div>
          </div>
        </div>

        <nav className={styles.nav}>
          {config.navSections.map((section, si) => (
            <div key={si}>
              {section.title && (
                <div className={styles.navSection}>{section.title}</div>
              )}
              {section.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === config.basePath}
                  className={({ isActive }) =>
                    `${styles.navLink} ${isActive ? styles.navLinkActive : ""}`
                  }
                >
                  <item.icon size={20} />
                  {item.label}
                </NavLink>
              ))}
            </div>
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

      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  );
}
