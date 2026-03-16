import { Home, FileText, ClipboardList, Calendar } from "lucide-react";
import PortalLayout from "@/shared/components/PortalLayout";
import type { PortalConfig } from "@/shared/components/PortalLayout";

const config: PortalConfig = {
  portalName: "Portal do Aluno",
  sidebarColor: "#636e72",
  accentColor: "#0984e3",
  basePath: "/aluno",
  navSections: [
    {
      items: [
        { to: "/aluno", icon: Home, label: "Dashboard" },
        { to: "/aluno/boletim", icon: FileText, label: "Boletim" },
        { to: "/aluno/faltas", icon: ClipboardList, label: "Faltas" },
        { to: "/aluno/horario", icon: Calendar, label: "Horario" },
      ],
    },
  ],
};

export default function AlunoLayout() {
  return <PortalLayout config={config} />;
}
