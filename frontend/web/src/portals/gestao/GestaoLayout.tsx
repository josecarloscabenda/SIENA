import {
  BookOpen, Calendar, ClipboardList, FileText, Home,
  KeyRound, LayoutGrid, School, UserCheck, Users, Users2,
} from "lucide-react";
import PortalLayout from "@/shared/components/PortalLayout";
import type { PortalConfig } from "@/shared/components/PortalLayout";

const config: PortalConfig = {
  portalName: "Gestao Escolar",
  sidebarColor: "#1A3F7A",
  accentColor: "#00A878",
  basePath: "/gestao",
  navSections: [
    {
      items: [
        { to: "/gestao", icon: Home, label: "Dashboard" },
      ],
    },
    {
      title: "Pessoas",
      items: [
        { to: "/gestao/alunos", icon: Users, label: "Alunos" },
        { to: "/gestao/professores", icon: Users2, label: "Professores" },
        { to: "/gestao/encarregados", icon: UserCheck, label: "Encarregados" },
      ],
    },
    {
      title: "Academico",
      items: [
        { to: "/gestao/matriculas", icon: FileText, label: "Matriculas" },
        { to: "/gestao/turmas", icon: LayoutGrid, label: "Turmas" },
        { to: "/gestao/curriculos", icon: BookOpen, label: "Curriculos" },
        { to: "/gestao/horarios", icon: Calendar, label: "Horarios" },
        { to: "/gestao/pauta", icon: ClipboardList, label: "Pauta" },
      ],
    },
    {
      title: "Escola",
      items: [
        { to: "/gestao/escola", icon: School, label: "Dados da Escola" },
        { to: "/gestao/utilizadores", icon: KeyRound, label: "Utilizadores" },
      ],
    },
  ],
};

export default function GestaoLayout() {
  return <PortalLayout config={config} />;
}
