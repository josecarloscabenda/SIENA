import { Route, Routes } from "react-router-dom";
import ProfessorLayout from "./ProfessorLayout";
import DashboardProfessor from "./pages/DashboardProfessor";
import MinhasTurmas from "./pages/MinhasTurmas";
import Diario from "./pages/Diario";
import LancarNotas from "./pages/LancarNotas";
import MeuHorario from "./pages/MeuHorario";

export default function ProfessorRoutes() {
  return (
    <Routes>
      <Route element={<ProfessorLayout />}>
        <Route index element={<DashboardProfessor />} />
        <Route path="turmas" element={<MinhasTurmas />} />
        <Route path="diario" element={<Diario />} />
        <Route path="notas" element={<LancarNotas />} />
        <Route path="horario" element={<MeuHorario />} />
      </Route>
    </Routes>
  );
}
