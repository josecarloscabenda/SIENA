import { Home, School } from "lucide-react";
import PortalLayout from "@/shared/components/PortalLayout";
import type { PortalConfig } from "@/shared/components/PortalLayout";

const config: PortalConfig = {
  portalName: "Administracao",
  sidebarColor: "#1a1a2e",
  accentColor: "#e94560",
  basePath: "/admin",
  navSections: [
    {
      items: [
        { to: "/admin", icon: Home, label: "Dashboard" },
        { to: "/admin/escolas", icon: School, label: "Escolas / Tenants" },
      ],
    },
  ],
};

export default function AdminLayout() {
  return <PortalLayout config={config} />;
}
