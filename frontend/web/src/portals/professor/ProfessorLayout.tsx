import { Home, LayoutGrid, ClipboardList, FileText, Calendar } from "lucide-react";
import PortalLayout from "@/shared/components/PortalLayout";
import type { PortalConfig } from "@/shared/components/PortalLayout";

const config: PortalConfig = {
  portalName: "Portal Professor",
  sidebarColor: "#2d3436",
  accentColor: "#6c5ce7",
  basePath: "/professor",
  navSections: [
    {
      items: [
        { to: "/professor", icon: Home, label: "Dashboard" },
        { to: "/professor/turmas", icon: LayoutGrid, label: "Minhas Turmas" },
        { to: "/professor/diario", icon: ClipboardList, label: "Diario" },
        { to: "/professor/notas", icon: FileText, label: "Notas" },
        { to: "/professor/horario", icon: Calendar, label: "Meu Horario" },
      ],
    },
  ],
};

export default function ProfessorLayout() {
  return <PortalLayout config={config} />;
}
