import { Home, Users } from "lucide-react";
import PortalLayout from "@/shared/components/PortalLayout";
import type { PortalConfig } from "@/shared/components/PortalLayout";

const config: PortalConfig = {
  portalName: "Portal do Encarregado",
  sidebarColor: "#4a4a4a",
  accentColor: "#e17055",
  basePath: "/encarregado",
  navSections: [
    {
      items: [
        { to: "/encarregado", icon: Home, label: "Dashboard" },
        { to: "/encarregado/filhos", icon: Users, label: "Meus Educandos" },
      ],
    },
  ],
};

export default function EncarregadoLayout() {
  return <PortalLayout config={config} />;
}
